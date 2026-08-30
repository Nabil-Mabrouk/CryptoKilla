import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Footer from "./Footer";

// Passthrough i18n, même patron que Navbar.test.tsx : Footer utilise
// désormais useTranslation() pour le bandeau disclaimer (Livre, chapitre
// 25, N-C25-07).
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: "fr", changeLanguage: vi.fn() },
  }),
}));

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

describe("Footer", () => {
  it("affiche le copyright avec le nom du projet (lu via /health) et l'année courante", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() => Promise.resolve(jsonResponse({ project: "pain-scraper" }))),
    );

    render(<Footer />);

    const year = new Date().getFullYear();
    await waitFor(() =>
      expect(screen.getByText(`© ${year} pain-scraper`)).toBeInTheDocument(),
    );
  });

  it("affiche le bandeau disclaimer permanent", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() => Promise.resolve(jsonResponse({ project: "pain-scraper" }))),
    );

    render(<Footer />);

    expect(screen.getByText("landing.disclaimer")).toBeInTheDocument();
  });
});
