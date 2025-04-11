"use client";
import { useState } from "react";
import { motion } from "framer-motion";

const productSuggestions = [
  {
    title: "Kit de Pintura Acrílica",
    price: "R$89",
    source: "Amazon",
    link: "https://www.amazon.com/kit-pintura"
  },
  {
    title: "Assinatura de Caixa Criativa",
    price: "R$59",
    source: "UauBox",
    link: "https://www.uaubox.com"
  },
  {
    title: "Curso Online de Aquarela",
    price: "R$120",
    source: "Hotmart",
    link: "https://www.hotmart.com"
  }
];

export default function ShoppingAssistant() {
  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState({ age: "", style: "" });
  const [name, setName] = useState("");

  const handleNext = () => setStep(step + 1);

  return (
    <div className="max-w-xl mx-auto p-4 space-y-6 font-sans">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="text-xl font-semibold text-center"
      >
        {step === 0 && "Qual o nome da pessoa que vai receber o presente?"}
        {step === 1 && `Qual a idade de ${name}?`}
        {step === 2 && `Qual o estilo de ${name}?`}
        {step === 3 && `Sugestões com base no estilo ${profile.style}:`}
      </motion.div>

      {step === 0 && (
        <div className="flex gap-2">
          <input
            className="flex-1 p-2 border rounded-xl"
            placeholder="Ex: Ana"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button
            onClick={handleNext}
            disabled={!name}
            className="bg-black text-white rounded-xl px-4 py-2"
          >
            Avançar
          </button>
        </div>
      )}

      {step === 1 && (
        <div className="flex gap-2">
          <input
            className="flex-1 p-2 border rounded-xl"
            placeholder="Ex: 25"
            value={profile.age}
            onChange={(e) => setProfile({ ...profile, age: e.target.value })}
          />
          <button
            onClick={handleNext}
            disabled={!profile.age}
            className="bg-black text-white rounded-xl px-4 py-2"
          >
            Avançar
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="grid grid-cols-2 gap-2">
          {["Criativa", "Minimalista", "Romântica", "Aventureira"].map((style) => (
            <button
              key={style}
              onClick={() => {
                setProfile({ ...profile, style });
                handleNext();
              }}
              className={`rounded-xl border px-4 py-2 ${
                profile.style === style ? "bg-black text-white" : ""
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          {productSuggestions.map((product) => (
            <div
              key={product.title}
              className="border rounded-2xl shadow p-4 space-y-1"
            >
              <div className="font-semibold text-lg">{product.title}</div>
              <div className="text-gray-500">
                {product.price} – {product.source}
              </div>
              <a
                href={product.link}
                className="text-blue-500 hover:underline text-sm"
                target="_blank"
                rel="noopener noreferrer"
              >
                Ver produto
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
