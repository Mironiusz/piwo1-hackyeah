/**
 * A text of the interface cut after its first sentence: the lead, which a page of text sets in bold as the name of an item,
 * and the rest, which keeps the space that parted the two.
 */
export interface LeadSplit {
  lead: string;
  rest: string;
}

/**
 * A text of the interface cut around one of its parts, so a view can draw that part as a mark.
 */
export interface PartSplit {
  before: string;
  after: string;
}

const SENTENCE_END = ". ";

/**
 * Cuts a text after its first sentence. A text of one sentence has no lead and comes back whole as the rest.
 */
export function splitLeadSentence(text: string): LeadSplit {
  const end = text.indexOf(SENTENCE_END);
  if (end === -1) {
    return { lead: "", rest: text };
  }
  return { lead: text.slice(0, end + 1), rest: text.slice(end + 1) };
}

/**
 * Cuts a text around the first place where a part stands in it. Returns null when the text does not hold the part.
 */
export function splitAroundPart(text: string, part: string): PartSplit | null {
  const start = part === "" ? -1 : text.indexOf(part);
  if (start === -1) {
    return null;
  }
  return { before: text.slice(0, start), after: text.slice(start + part.length) };
}
