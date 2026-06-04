import torch
import torch.nn as nn
import torch.nn.functional as F

class GATLayer(nn.Module):
    """
    Enhanced GAT layer with BatchNorm and Residuals.
    """
    def __init__(self, in_features, out_features, n_heads=8, dropout=0.2):
        super(GATLayer, self).__init__()
        self.n_heads = n_heads
        self.out_features = out_features

        self.W = nn.Linear(in_features, n_heads * out_features, bias=False)
        self.a = nn.Parameter(torch.empty(size=(n_heads, 2 * out_features, 1)))
        nn.init.xavier_uniform_(self.a.data, gain=1.414)

        self.leakyrelu = nn.LeakyReLU(0.2)
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.BatchNorm1d(21) # Batch norm over nodes
        
        if in_features != n_heads * out_features:
            self.skip = nn.Linear(in_features, n_heads * out_features)
        else:
            self.skip = nn.Identity()

    def forward(self, h, adj):
        batch_size, N, _ = h.size()
        residual = self.skip(h)

        h_prime = self.W(h).view(batch_size, N, self.n_heads, self.out_features)
        h_prime = h_prime.permute(0, 2, 1, 3) 

        a_i = self.a[:, :self.out_features, :]
        a_j = self.a[:, self.out_features:, :]
        f_i = torch.matmul(h_prime, a_i)
        f_j = torch.matmul(h_prime, a_j)
        e = self.leakyrelu(f_i + f_j.transpose(-1, -2))

        adj_expanded = adj.unsqueeze(0).unsqueeze(0)
        zero_vec = -9e15 * torch.ones_like(e)
        attention = torch.where(adj_expanded > 0, e, zero_vec)
        attention = F.softmax(attention, dim=-1)
        attention = self.dropout(attention)

        h_res = torch.matmul(attention, h_prime)
        h_res = h_res.permute(0, 2, 1, 3).reshape(batch_size, N, self.n_heads * self.out_features)
        
        return F.elu(self.norm(h_res + residual))

class MistralGAT(nn.Module):
    """
    Highly enhanced GAT for Mistral 7B.
    - Node features = [AIE, Mean, Std, Range, Kurt, Skew, Pos] (7 features)
    - Fully connected graph
    - 3 GAT layers with residual connections
    """
    def __init__(self, node_in=1, global_in=5, hidden_dim=32, n_heads=8):
        super(MistralGAT, self).__init__()
        
        # Total node features = 1 (AIE) + 5 (Global Stats) + 1 (Pos Index) = 7
        total_node_in = node_in + global_in + 1
        
        self.gat1 = GATLayer(total_node_in, hidden_dim, n_heads=n_heads)
        self.gat2 = GATLayer(hidden_dim * n_heads, hidden_dim, n_heads=n_heads)
        self.gat3 = GATLayer(hidden_dim * n_heads, hidden_dim, n_heads=1) # Reduce to single representation

        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128), # Mean + Max pooling
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 2)
        )

        self.register_buffer('adj', torch.ones(21, 21))
        # Precompute positional indices [0, 1, ..., 20]
        self.register_buffer('pos_indices', torch.arange(21).float().unsqueeze(0).unsqueeze(-1) / 20.0)

    def forward(self, layer_aie, global_stats):
        # layer_aie: (batch, 21)
        # global_stats: (batch, 5)
        batch_size = layer_aie.size(0)

        # 1. Broadcast global stats to each of the 21 nodes
        # global_expanded: (batch, 21, 5)
        global_expanded = global_stats.unsqueeze(1).expand(-1, 21, -1)
        
        # 2. Add AIE and Positional Encoding
        # x: (batch, 21, 7)
        pos = self.pos_indices.expand(batch_size, -1, -1)
        x = torch.cat([layer_aie.unsqueeze(-1), global_expanded, pos], dim=-1)

        # 3. GAT processing
        x = self.gat1(x, self.adj)
        x = self.gat2(x, self.adj)
        x = self.gat3(x, self.adj)

        # 4. Global Pooling
        mean_pool = x.mean(dim=1)
        max_pool, _ = x.max(dim=1)
        graph_feat = torch.cat([mean_pool, max_pool], dim=1)

        return self.classifier(graph_feat)


