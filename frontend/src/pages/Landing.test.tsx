import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

// Landing (Chap 27, identité CryptoKilla) n'assemble plus les blocs
// génériques Studio depuis landing-manifest.json (skin/blocks) — passthrough
// i18n comme les autres tests (App.test.tsx, Navbar.test.tsx) pour asserter
// sur les clés plutôt que sur une traduction chargée en vrai.
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: "fr", changeLanguage: vi.fn() },
  }),
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => ({ user: null, logout: vi.fn() }),
}));

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

vi.stubGlobal(
  "fetch",
  vi.fn().mockImplementation((url: string) => {
    if (String(url).includes("/health")) {
      return Promise.resolve(jsonResponse({ project: "cryptokilla", modules: {} }));
    }
    return Promise.resolve(jsonResponse({}));
  }),
);

// landing-manifest.json réel du projet (project/domain seulement encore
// lus par Landing.tsx, pour EmailCapture) — pas besoin de le mocker.
import Landing from "./Landing";

describe("Landing", () => {
  it("rend le hero, les 4 sections réservées, la liste d'attente, et le Footer", async () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText("cryptokilla")).toBeInTheDocument());
    expect(screen.getByText("landing.hero.title")).toBeInTheDocument();
    expect(screen.getByText("landing.killa.empty")).toBeInTheDocument();
    expect(screen.getByText("landing.chat.empty")).toBeInTheDocument();
    expect(screen.getByText("landing.leaderboard.empty")).toBeInTheDocument();
    expect(screen.getByText("landing.dynasties.empty")).toBeInTheDocument();
    expect(screen.getByText("landing.waitlist.headline")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByTestId("footer-copyright").textContent).toMatch(/© \d{4} cryptokilla/),
    );
  });

  it("affiche le bandeau disclaimer permanent (Livre, chapitre 25, N-C25-07)", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>,
    );
    expect(screen.getByText("landing.disclaimer")).toBeInTheDocument();
  });

  it("pose un repère stable sur la racine pour les tests de routage", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("landing-page")).toHaveClass("landing");
  });
});
