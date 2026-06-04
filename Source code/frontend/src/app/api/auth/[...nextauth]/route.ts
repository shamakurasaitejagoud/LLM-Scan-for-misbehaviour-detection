import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { MongoDBAdapter } from "@auth/mongodb-adapter";
import clientPromise from "@/lib/mongodb";
import * as jwt from "jsonwebtoken";

const NEXTAUTH_SECRET = process.env.NEXTAUTH_SECRET || "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;
        
        const client = await clientPromise;
        const usersCollection = client.db("llmscan").collection("users");
        
        const user = await usersCollection.findOne({ email: credentials.email });
        if (!user || !user.password) return null; // user.password is missing if they signed up with Google

        const bcrypt = require("bcryptjs");
        const isValid = await bcrypt.compare(credentials.password, user.password);
        
        if (!isValid) return null;

        return { id: user._id.toString(), email: user.email, name: user.name };
      },
    }),
  ],
  adapter: MongoDBAdapter(clientPromise) as any,
  session: {
    strategy: "jwt",
  },
  jwt: {
    // We encode the JWT standardly so FastAPI can decode it
    encode: async ({ secret, token, maxAge }) => {
      const encodedToken = jwt.sign(token!, NEXTAUTH_SECRET, {
        algorithm: "HS256",
      });
      return encodedToken;
    },
    decode: async ({ secret, token }) => {
      if (!token) return null;
      try {
        const decoded = jwt.verify(token, NEXTAUTH_SECRET, {
          algorithms: ["HS256"],
        });
        return decoded as any;
      } catch (e) {
        return null;
      }
    },
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user && token) {
        // Sign the token object so the frontend has the raw JWT string to send to FastAPI
        const encodedToken = jwt.sign(token, NEXTAUTH_SECRET, { algorithm: "HS256" });
        (session as any).accessToken = encodedToken;
      }
      return session;
    },
  },
  secret: NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
