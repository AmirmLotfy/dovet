import { describe, expect, it } from "vitest";

describe("console", () => {
  it("does not invent progress percentages", () => {
    expect("No protected work yet").not.toMatch(/\d+%/);
  });
});

