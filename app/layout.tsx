export const metadata = {
  title: 'Assistente de Compras',
  description: 'Um assistente para encontrar presentes perfeitos',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-white text-black min-h-screen">{children}</body>
    </html>
  );
}
