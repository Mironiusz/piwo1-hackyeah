import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import { AMENITY_TYPES, BARRIER_TYPES, type FactType } from "../api/types.ts";
import { Button } from "../parts/Button.tsx";
import { Icon } from "../parts/Icon.tsx";
import type { IconName } from "../parts/iconPaths.ts";
import { Note } from "../parts/Note.tsx";
import { ACTIONS, ACTIONS_ONE, HINT, PAGE_HEADING, PAGE_LEAD, PAGE_TITLE } from "../parts/styles.ts";
import { readLastMapPath } from "../state/lastMapPath.ts";
import { NEEDS_PRESETS, useNeeds, type NeedsPresetId } from "../state/needs.tsx";

const PRESETS: readonly { id: NeedsPresetId; icon: IconName }[] = [
  { id: "wheelchair", icon: "preset_wheelchair" },
  { id: "stroller", icon: "preset_stroller" },
  { id: "walking", icon: "preset_walking" },
];

interface ItemListProps {
  types: readonly FactType[];
  isSet: (type: FactType) => boolean;
  onToggle: (type: FactType) => void;
}

/**
 * The items of one group of the needs as checkboxes, each with its icon and its name.
 */
function ItemList({ types, isSet, onToggle }: ItemListProps) {
  const { t } = useTranslation();
  return (
    <ul className="border-b border-line">
      {types.map((type) => (
        <li key={type} className="border-t border-line">
          <label className="flex min-h-12 items-center gap-3 py-1.5">
            <input type="checkbox" checked={isSet(type)} onChange={() => onToggle(type)} className="m-0 size-[22px] flex-none accent-shell" />
            <Icon name={type} className="text-muted" />
            <span>{t(`type.${type}`)}</span>
          </label>
        </li>
      ))}
    </ul>
  );
}

/**
 * The needs of a person: the three presets, the five barriers to avoid and the six amenities needed.
 * A preset only sets the items and never stays chosen. The needs stay on the device.
 * On the first opening the view can be skipped; later it only has the way back.
 */
export function NeedsView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { needs, toggleItem, applyPreset, markSeen } = useNeeds();
  const [isFirstOpening] = useState(!needs.isSeen);
  const [appliedPreset, setAppliedPreset] = useState<NeedsPresetId | null>(null);

  const leave = () => {
    markSeen();
    void navigate(isFirstOpening ? "/" : readLastMapPath());
  };

  const pickPreset = (presetId: NeedsPresetId) => {
    applyPreset(presetId);
    setAppliedPreset(presetId);
  };

  const toggle = (type: FactType) => {
    toggleItem(type);
    setAppliedPreset(null);
  };

  const hasNoBarrier = needs.avoid.length === 0;
  const hasNoItem = hasNoBarrier && needs.need.length === 0;

  return (
    <>
      <h1 className={PAGE_TITLE}>{t("needs.title")}</h1>
      <p className={PAGE_LEAD}>{t("needs.intro")}</p>

      <h2 className={`${PAGE_HEADING} mt-0!`}>{t("needs.presets")}</h2>
      <div className="grid gap-2">
        {PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            onClick={() => pickPreset(preset.id)}
            className="flex min-h-12 items-center gap-2.5 rounded-panel border-[1.5px] border-shell bg-white px-3 py-2 text-left font-semibold text-shell"
          >
            <Icon name={preset.icon} />
            {t(`needs.preset.${preset.id}`)}
          </button>
        ))}
      </div>
      <output className="sr-only">
        {appliedPreset !== null
          ? t("needs.preset.applied", {
              barriers: t("count.barriers", { count: NEEDS_PRESETS[appliedPreset].avoid.length }),
              amenities: t("count.amenities", { count: NEEDS_PRESETS[appliedPreset].need.length }),
            })
          : ""}
      </output>

      <h2 className={PAGE_HEADING}>{t("needs.avoid")}</h2>
      <ItemList types={BARRIER_TYPES} isSet={(type) => (needs.avoid as readonly FactType[]).includes(type)} onToggle={toggle} />

      <h2 className={PAGE_HEADING}>{t("needs.need")}</h2>
      <ItemList types={AMENITY_TYPES} isSet={(type) => (needs.need as readonly FactType[]).includes(type)} onToggle={toggle} />

      {hasNoBarrier ? (
        <Note kind="dash" announce="status" className="mt-4">
          <p>{t("needs.no_barrier")}</p>
          {hasNoItem ? <p className="mt-1">{t("needs.empty")}</p> : null}
        </Note>
      ) : null}

      <div className={isFirstOpening ? ACTIONS : ACTIONS_ONE}>
        {isFirstOpening ? <Button onClick={leave}>{t("needs.skip")}</Button> : null}
        <Button look="primary" onClick={leave}>
          {t("needs.done")}
        </Button>
      </div>
      {hasNoBarrier ? null : <p className={`${HINT} mt-2.5`}>{t("needs.no_barrier")}</p>}
    </>
  );
}
