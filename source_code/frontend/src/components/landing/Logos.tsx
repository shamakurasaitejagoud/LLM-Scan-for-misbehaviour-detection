export function Logos() {
  const logos = [
    { name: "Outshort", opacity: "opacity-40" },
    { name: "SUPERNOVA", opacity: "opacity-60" },
    { name: "Wharf", opacity: "opacity-50" },
    { name: "brendi", opacity: "opacity-50" },
    { name: "Stably", opacity: "opacity-60" },
    { name: "zuma", opacity: "opacity-40" },
    { name: "hurb", opacity: "opacity-50" },
  ];

  return (
    <section className="py-12 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p className="text-sm font-medium text-gray-400 mb-8 tracking-wider uppercase">Trusted by innovative teams</p>
        <div className="flex flex-wrap justify-center gap-8 md:gap-16 items-center">
          {logos.map((logo, index) => (
            <div key={index} className={`text-xl font-black tracking-tighter grayscale ${logo.opacity} hover:opacity-100 hover:grayscale-0 transition-all duration-300 cursor-pointer`}>
              {logo.name}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
