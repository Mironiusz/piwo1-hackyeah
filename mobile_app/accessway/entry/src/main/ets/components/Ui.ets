import { tr } from '../model/I18n';
import { factTitle, formatDate, statusLabel, streetLabel } from '../model/Labels';
import { Fact, FactSource, FactStatus } from '../model/Types';
import { formatDistance } from '../domain/Geo';
import { KindIcon } from './Glyphs';
import { FONT, FONT_B, FONT_TITLE, fs, P, RADIUS, RADIUS_CTRL, TOUCH } from './Theme';

@Component
export struct Icon {
  @Prop name: string = 'info';
  @Prop iconSize: number = 24;
  @Prop color: string = '#000000';

  build() {
    Image($rawfile(`icons/${this.name}.svg`))
      .width(this.iconSize)
      .height(this.iconSize)
      .fillColor(this.color)
      .objectFit(ImageFit.Contain)
      .accessibilityLevel('no')
  }
}

export enum BtnKind {
  PRIMARY = 'primary',
  OUTLINE = 'outline',
  GRAY = 'gray',
  YELLOW = 'yellow',
  DANGER = 'danger'
}

/**
 * Buttons from the system artboard: Wyznacz trasę (Plan route), Wróć (Back), Nadal jest (Still there, gray),
 * Zgłoś (Report, yellow) and the red Usuń konto (Delete account).
 */
@Component
export struct Btn {
  @Prop label: string = '';
  @Prop kind: BtnKind = BtnKind.PRIMARY;
  @Prop icon: string = '';
  @Prop small: boolean = false;
  @Prop enabledState: boolean = true;
  @Prop a11y: string = '';
  action: () => void = () => {
  };

  private fg(): string {
    if (this.kind === BtnKind.OUTLINE) {
      return P().primary;
    }
    if (this.kind === BtnKind.GRAY) {
      return P().grayText;
    }
    if (this.kind === BtnKind.YELLOW) {
      return P().onYellow;
    }
    return '#FFFFFF';
  }

  private bg(): string {
    if (this.kind === BtnKind.OUTLINE) {
      return P().card;
    }
    if (this.kind === BtnKind.GRAY) {
      return P().gray;
    }
    if (this.kind === BtnKind.YELLOW) {
      return P().yellow;
    }
    if (this.kind === BtnKind.DANGER) {
      return P().barrier;
    }
    return P().primary;
  }

  private edgeColor(): string {
    if (this.kind === BtnKind.OUTLINE) {
      return P().primary;
    }
    if (this.kind === BtnKind.GRAY) {
      return P().outlineVar;
    }
    return this.bg();
  }

  build() {
    Button({ type: ButtonType.Normal }) {
      Row({ space: 8 }) {
        if (this.icon.length > 0) {
          Icon({ name: this.icon, iconSize: this.small ? 18 : 20, color: this.fg() })
        }
        Text(this.label)
          .fontFamily(FONT_B)
          .fontSize(fs(this.small ? 13.5 : 15))
          .fontColor(this.fg())
          .textAlign(TextAlign.Center)
          .maxLines(2)
      }
      .justifyContent(FlexAlign.Center)
      .padding({ left: this.small ? 12 : 16, right: this.small ? 12 : 16 })
    }
    .width(this.small ? 'auto' : '100%')
    .height(this.small ? 40 : 46)
    .borderRadius(RADIUS)
    .backgroundColor(this.bg())
    .border({ width: this.kind === BtnKind.OUTLINE ? 1.5 : 1, color: this.edgeColor() })
    .enabled(this.enabledState)
    .accessibilityText(this.a11y.length > 0 ? this.a11y : this.label)
    .onClick(() => this.action())
  }
}

/** Link from the mockup: navy, bold and underlined; a red variant for account deletion. */
@Component
export struct LinkText {
  @Prop label: string = '';
  @Prop danger: boolean = false;
  @Prop textSize: number = 14;
  action: () => void = () => {
  };

  build() {
    Text(this.label)
      .fontFamily(FONT_B)
      .fontSize(fs(this.textSize))
      .fontColor(this.danger ? P().barrier : P().primary)
      .decoration({ type: TextDecorationType.Underline, color: this.danger ? P().barrier : P().primary })
      .padding({ top: 6, bottom: 6, right: 4 })
      .focusable(true)
      .accessibilityRole(AccessibilityRoleType.BUTTON)
      .onClick(() => this.action())
  }
}

@Component
export struct BackLink {
  action: () => void = () => {
  };

  build() {
    Row({ space: 4 }) {
      Icon({ name: 'chevron_left', iconSize: 20, color: P().primary })
      Text(tr('Wróć', 'Back')).fontFamily(FONT_B).fontSize(fs(14)).fontColor(P().primary)
    }
    .height(TOUCH)
    .focusable(true)
    .accessibilityGroup(true)
    .accessibilityText(tr('Wróć', 'Back'))
    .onClick(() => this.action())
  }
}

@Component
export struct SampleChip {
  build() {
    Text(tr('dane przykładowe', 'sample data'))
      .fontFamily(FONT_B)
      .fontSize(fs(11.5))
      .fontColor(P().text)
      .padding({ left: 7, right: 7, top: 3, bottom: 3 })
      .borderRadius(RADIUS_CTRL)
      .backgroundColor(P().chipBg)
      .border({ width: 1, color: P().outlineVar })
  }
}

export function statusIcon(s: FactStatus): string {
  if (s === FactStatus.CONFIRMED) {
    return 'check';
  }
  if (s === FactStatus.DISPUTED) {
    return 'disputed';
  }
  return 'error_circle';
}

export function statusColor(s: FactStatus): string {
  if (s === FactStatus.CONFIRMED) {
    return P().clear;
  }
  if (s === FactStatus.DISPUTED) {
    return P().disputed;
  }
  return P().text;
}

/**
 * Fact source and date as in the mockup rows: "zgłoszenie, 3.10.2026" (report, 3.10.2026) or
 * "OpenStreetMap, edycja 12.05.2025" (OpenStreetMap, edit 12.05.2025).
 */
export function sourceLine(f: Fact): string {
  if (f.source === FactSource.OSM) {
    return f.date > 0 ? tr(`OpenStreetMap, edycja ${formatDate(f.date)}`, `OpenStreetMap, edited ${formatDate(f.date)}`) :
      'OpenStreetMap';
  }
  return tr(`zgłoszenie, ${formatDate(f.date)}`, `report, ${formatDate(f.date)}`);
}

@Component
export struct StatusBadge {
  @Prop status: FactStatus = FactStatus.UNVERIFIED;

  build() {
    Row({ space: 4 }) {
      Icon({ name: statusIcon(this.status), iconSize: 15, color: statusColor(this.status) })
      Text(statusLabel(this.status)).fontFamily(FONT_B).fontSize(fs(13)).fontColor(statusColor(this.status))
    }
  }
}

/** Status, source with date and the sample data mark in a single wrapping row. */
@Component
export struct StatusLine {
  fact: Fact | null = null;

  build() {
    if (this.fact !== null) {
      Flex({ wrap: FlexWrap.Wrap, alignItems: ItemAlign.Center }) {
        StatusBadge({ status: (this.fact as Fact).status }).margin({ right: 8, top: 3, bottom: 3 })
        Text(sourceLine(this.fact as Fact)).fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar)
          .margin({ right: 8, top: 3, bottom: 3 })
        if ((this.fact as Fact).isSample) {
          SampleChip().margin({ top: 3, bottom: 3 })
        }
      }
    }
  }
}

/** Fact list row: kind glyph, title, distance, street and status row. */
@Component
export struct FactRow {
  fact: Fact | null = null;
  distanceM: number = -1;
  distanceText: string = '';
  showLine: boolean = true;
  onOpen: (id: string) => void = () => {
  };

  build() {
    if (this.fact !== null) {
      Row({ space: 12 }) {
        KindIcon({ kind: (this.fact as Fact).kind, category: (this.fact as Fact).category, iconSize: 20, color: P().text })
          .margin({ top: 2 })
        Column({ space: 3 }) {
          Row({ space: 8 }) {
            Text(factTitle((this.fact as Fact).kind, (this.fact as Fact).category, (this.fact as Fact).stepCount,
              (this.fact as Fact).radiusM))
              .fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text).layoutWeight(1)
            if (this.distanceText.length > 0 || this.distanceM >= 0) {
              Text(this.distanceText.length > 0 ? this.distanceText : formatDistance(this.distanceM))
                .fontFamily(FONT_B).fontSize(fs(14)).fontColor(P().text)
            }
          }
          .width('100%')
          .alignItems(VerticalAlign.Top)
          if ((this.fact as Fact).street.length > 0) {
            Text(streetLabel((this.fact as Fact).street)).fontFamily(FONT).fontSize(fs(13)).fontColor(P().textVar)
          }
          StatusLine({ fact: this.fact }).margin({ top: 2 })
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)
      }
      .width('100%')
      .alignItems(VerticalAlign.Top)
      .padding({ top: 12, bottom: 12 })
      .border({ width: { bottom: this.showLine ? 1 : 0 }, color: P().outlineVar })
      .focusable(true)
      .accessibilityGroup(true)
      .onClick(() => this.onOpen((this.fact as Fact).id))
    }
  }
}

/** Group header with a counter: "Z Twoich potrzeb 2" (From your needs 2). */
@Component
export struct GroupHeader {
  @Prop title: string = '';
  @Prop count: string = '';

  build() {
    Row({ space: 8 }) {
      Text(this.title).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text).accessibilityLevel('yes')
      if (this.count.length > 0) {
        Text(this.count).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar)
      }
      Blank()
    }
    .width('100%')
    .padding({ top: 18, bottom: 8 })
    .border({ width: { bottom: 1 }, color: P().outlineVar })
  }
}

export enum BoxKind {
  ERROR = 'error',
  GAP = 'gap',
  INFO = 'info'
}

/** Messages from the mockup: error with a black border, data gap with a dashed border and info with a light border. */
@Component
export struct MessageBox {
  @Prop lead: string = '';
  @Prop text: string = '';
  @Prop kind: BoxKind = BoxKind.INFO;

  build() {
    Text() {
      if (this.lead.length > 0) {
        Span(this.lead + ' ').fontFamily(FONT_B).fontColor(P().text)
      }
      Span(this.text).fontFamily(FONT).fontColor(P().text)
    }
    .fontSize(fs(13.5))
    .lineHeight(fs(19))
    .width('100%')
    .padding({ left: 14, right: 14, top: 11, bottom: 11 })
    .borderRadius(RADIUS)
    .backgroundColor(P().card)
    .border({
      width: this.kind === BoxKind.ERROR ? 1.5 : 1,
      color: this.kind === BoxKind.ERROR ? P().text : (this.kind === BoxKind.GAP ? P().noData : P().outlineVar),
      style: this.kind === BoxKind.GAP ? BorderStyle.Dashed : BorderStyle.Solid
    })
    .accessibilityLevel('yes')
  }
}

/** Segmented switch: the selected part is navy, the others are white with navy text. */
@Component
export struct Segmented {
  @Prop options: string[] = [];
  @Prop selected: number = 0;
  onSelect: (i: number) => void = () => {
  };

  build() {
    Row() {
      ForEach(this.options, (o: string, i: number) => {
        Text(o)
          .fontFamily(FONT_B)
          .fontSize(fs(13.5))
          .fontColor(i === this.selected ? '#FFFFFF' : P().primary)
          .backgroundColor(i === this.selected ? P().primary : P().card)
          .textAlign(TextAlign.Center)
          .height('100%')
          .layoutWeight(1)
          .border({ width: { left: i > 0 ? 1 : 0 }, color: P().primary })
          .focusable(true)
          .accessibilityRole(AccessibilityRoleType.RADIO)
          .accessibilitySelected(i === this.selected)
          .onClick(() => this.onSelect(i))
      }, (o: string, i: number) => `${i}-${o}-${this.selected}`)
    }
    .width('100%')
    .height(40)
    .borderRadius(RADIUS)
    .border({ width: 1.5, color: P().primary })
    .clip(true)
  }
}

/** Label and value pair in fact details and in the report summary. */
@Component
export struct KeyValue {
  @Prop name: string = '';
  @Prop value: string = '';
  @Prop keyWidth: number = 132;
  @Prop valueColor: string = '';

  build() {
    Row() {
      Text(this.name).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).width(this.keyWidth)
      Text(this.value).fontFamily(FONT_B).fontSize(fs(13.5))
        .fontColor(this.valueColor.length > 0 ? this.valueColor : P().text).layoutWeight(1)
    }
    .width('100%')
    .alignItems(VerticalAlign.Top)
    .padding({ top: 4, bottom: 4 })
  }
}

/** 23 px page title and the description below it. */
@Component
export struct PageTitle {
  @Prop title: string = '';
  @Prop intro: string = '';

  build() {
    Column({ space: 6 }) {
      Text(this.title).fontFamily(FONT_TITLE).fontSize(fs(23)).fontColor(P().text).accessibilityLevel('yes')
      if (this.intro.length > 0) {
        Text(this.intro).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).lineHeight(fs(19))
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.Start)
  }
}

/** Sheet header with a close button: "Krok 1 z 5" (Step 1 of 5) above the panel title. */
@Component
export struct SheetTitle {
  @Prop title: string = '';
  @Prop step: string = '';
  @Prop showClose: boolean = true;
  onClose: () => void = () => {
  };

  build() {
    Row() {
      Column({ space: 2 }) {
        if (this.step.length > 0) {
          Text(this.step).fontFamily(FONT_B).fontSize(fs(12.5)).fontColor(P().textVar)
        }
        Text(this.title).fontFamily(FONT_TITLE).fontSize(fs(19)).fontColor(P().text).accessibilityLevel('yes')
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)
      if (this.showClose) {
        Button({ type: ButtonType.Normal }) {
          Icon({ name: 'close_thin', iconSize: 22, color: P().text })
        }
        .width(TOUCH).height(TOUCH).backgroundColor(Color.Transparent)
        .accessibilityText(tr('Zamknij', 'Close'))
        .onClick(() => this.onClose())
      }
    }
    .width('100%')
    .alignItems(VerticalAlign.Center)
  }
}

/** Sheet handle above the map. */
@Component
export struct SheetHandle {
  build() {
    Row() {
      Divider().strokeWidth(4).color(P().outlineVar).width(36).lineCap(LineCapStyle.Round)
    }
    .width('100%')
    .justifyContent(FlexAlign.Center)
    .padding({ top: 8, bottom: 6 })
    .accessibilityLevel('no')
  }
}

/** Bullet list with a dash, as on the privacy and data pages. */
@Component
export struct Bullet {
  @Prop lead: string = '';
  @Prop text: string = '';

  build() {
    Row({ space: 10 }) {
      Text('–').fontFamily(FONT_B).fontSize(fs(14)).fontColor(P().text)
      Text() {
        if (this.lead.length > 0) {
          Span(this.lead + ' ').fontFamily(FONT_B)
        }
        Span(this.text).fontFamily(FONT)
      }
      .fontSize(fs(14))
      .fontColor(P().text)
      .lineHeight(fs(20))
      .layoutWeight(1)
    }
    .width('100%')
    .alignItems(VerticalAlign.Top)
  }
}

@Component
export struct SubTitle {
  @Prop text: string = '';

  build() {
    Text(this.text).fontFamily(FONT_B).fontSize(fs(14.5)).fontColor(P().text).margin({ top: 14 })
      .accessibilityLevel('yes')
  }
}

export const RADIUS_BTN: number = RADIUS;

@Builder
function noContent() {
}

/** White sheet with rounded top corners, overlapping the bottom edge of the map. */
@Component
export struct SheetBox {
  @Prop minHeight: number = 320;
  @BuilderParam content: () => void = noContent;

  build() {
    Column() {
      SheetHandle()
      this.content()
    }
    .width('100%')
    .constraintSize({ minHeight: this.minHeight })
    .padding({ left: 16, right: 16, bottom: 28 })
    .backgroundColor(P().card)
    .borderRadius({ topLeft: 16, topRight: 16 })
    .margin({ top: -16 })
    .shadow({ radius: 10, color: '#1F000000', offsetY: -2 })
    .alignItems(HorizontalAlign.Start)
  }
}

/** Page without a map: Wróć (Back) link, content and bottom margin. */
@Component
export struct PageBox {
  @BuilderParam content: () => void = noContent;

  build() {
    Scroll() {
      Column() {
        this.content()
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 6, bottom: 28 })
      .alignItems(HorizontalAlign.Start)
    }
    .width('100%')
    .height('100%')
    .align(Alignment.Top)
    .edgeEffect(EdgeEffect.None)
    .backgroundColor(P().card)
  }
}
