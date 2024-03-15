import React from "react";

function AboutUs() {
  return (
    <div className="mt-12 max-w-lg bg-[whitesmoke] p-6 shadow rounded text-center font-secondary mx-auto">
      <h1 className="font-[monospace] font-bold tracking-tight text-4xl">
        <span className="text-blue-500">DL4</span>
        <span className="text-orange-500">ML</span>
      </h1>
      <p className="text-gray-800 mt-4">
        Lorem ipsum dolor sit amet consectetur, adipisicing elit. Ipsam eligendi
        nemo nihil et aliquam iusto excepturi totam porro necessitatibus
        consequatur? In quibusdam, sed omnis delectus nihil, aliquid sit, sunt
        suscipit hic expedita amet dignissimos a quasi ullam nostrum vel labore?
      </p>
      <p className="mt-3 text-sm">
        E-mail: <span className="font-semibold">info@example.com</span>
      </p>
      <p className="text-sm">
        Phone: <span className="font-semibold">+1234567890</span>
      </p>
    </div>
  );
}

export default AboutUs;
