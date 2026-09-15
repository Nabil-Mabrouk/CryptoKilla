import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ChatPreview from "./ChatPreview";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ChatPreview", () => {
  it("affiche l'état vide (squelette) tant qu'aucune saison n'a de message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ season_id: null, messages: [] })));

    render(<ChatPreview />);

    expect(await screen.findByText("landing.chat.empty")).toBeInTheDocument();
  });

  it("interroge /api/arena/public/chat et affiche les vrais messages, jamais un propos inventé", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        season_id: "s1",
        messages: [
          {
            id: "m1",
            timestamp: "2026-09-15T14:00:00Z",
            dynasty: "Claude-Nord",
            color: "#4F46E5",
            generation: 3,
            text: "BTC casse la résistance des dernières 4h.",
            mentions: [],
            cites: [],
          },
        ],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<ChatPreview />);

    expect(await screen.findByText("BTC casse la résistance des dernières 4h.")).toBeInTheDocument();
    expect(screen.getByText("Claude-Nord-3")).toBeInTheDocument();
    expect(screen.queryByText("landing.chat.empty")).not.toBeInTheDocument();
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain("/api/arena/public/chat?limit=20");
  });
});
