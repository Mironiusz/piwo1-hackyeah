import { TEXT_LIST_ITEM } from "../parts/styles.ts";
import { splitLeadSentence } from "./textParts.ts";

/**
 * An item of a list on a page of text whose first sentence names the item and is set in bold, as the mocks of the pages draw it.
 */
export function LeadItem({ text }: { text: string }) {
  const { lead, rest } = splitLeadSentence(text);
  return (
    <li className={TEXT_LIST_ITEM}>
      {lead !== "" ? <b className="font-bold">{lead}</b> : null}
      {rest}
    </li>
  );
}
