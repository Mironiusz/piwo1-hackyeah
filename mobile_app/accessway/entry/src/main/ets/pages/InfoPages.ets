import { appModel } from '../data/AppModel';
import { tr } from '../model/I18n';
import { formatDate, statusLabel } from '../model/Labels';
import { FactStatus } from '../model/Types';
import { FONT, FONT_B, fs, P } from '../components/Theme';
import { BackLink, BoxKind, Bullet, MessageBox, PageBox, PageTitle, SampleChip, statusColor, statusIcon, SubTitle, Icon } from '../components/Ui';
import { Nav } from './Nav';

/** V-12: informacja o prywatności. */
@Component
export struct PrivacyView {
  nav: Nav = new Nav();

  build() {
    PageBox() {
      BackLink({ action: () => this.nav.back() })
      PageTitle({
        title: tr('Informacja o prywatności', 'Privacy information'),
        intro: tr('Co o Tobie przechowujemy, po co i jak długo, oraz czego nie przechowujemy.',
          'What we keep about you, why and for how long, and what we do not keep.')
      })
      SubTitle({ text: tr('Co przechowujemy', 'What we keep') })
      Column({ space: 8 }) {
        Bullet({ lead: tr('Pseudonim i hasło konta.', 'Account nickname and password.'),
          text: tr('Po to, żeby rozpoznać Twoje konto. Do chwili, gdy je usuniesz.',
            'To recognise your account. Until you delete it.') })
        Bullet({ lead: tr('Identyfikator głosu bez konta.', 'Vote identifier without an account.'),
          text: tr('Nieodwracalny skrót adresu IP i cech przeglądarki, żeby odróżnić jedną osobę bez konta od drugiej. Przez 30 dni od głosu. To dane osobowe w postaci spseudonimizowanej, nie dane anonimowe.',
            'An irreversible hash of the IP address and browser traits, to tell one person without an account from another. For 30 days after the vote. This is pseudonymised personal data, not anonymous data.') })
      }
      .margin({ top: 8 })
      SubTitle({ text: tr('Czego nie przechowujemy', 'What we do not keep') })
      Column({ space: 8 }) {
        Bullet({ lead: tr('Twoich potrzeb.', 'Your needs.'),
          text: tr('Zostają tylko na Twoim urządzeniu i nie są częścią konta.', 'They stay only on your device and are not part of the account.') })
        Bullet({ lead: tr('Bieżącej lokalizacji.', 'Your current location.'),
          text: tr('Używamy jej tylko do wyznaczenia jednej trasy.', 'We use it only to plan one route.') })
        Bullet({ lead: tr('Adresu e-mail.', 'E-mail address.'), text: tr('Nie pytamy o niego.', 'We do not ask for it.') })
        Bullet({ lead: tr('Informacji o niepełnosprawności.', 'Information about disability.'),
          text: tr('Nie pytamy o nią.', 'We do not ask about it.') })
      }
      .margin({ top: 8 })
      SubTitle({ text: tr('Kto jeszcze widzi Twoje dane', 'Who else sees your data') })
      Column({ space: 8 }) {
        Bullet({ text: tr('Twoja przeglądarka rozmawia tylko z naszym serwerem. Mapa, kroje pisma i skrypty pochodzą od nas, więc żadna zewnętrzna usługa nie poznaje Twojego adresu IP ani miejsca, które oglądasz.',
          'Your app talks only to our server. The map, fonts and scripts come from us, so no outside service learns your IP address or the place you look at.') })
        Bullet({ text: tr('Tekst wyszukiwania adresu przekazujemy zewnętrznej wyszukiwarce z naszego serwera, bez niczego, co Cię identyfikuje.',
          'We pass the address search text to an outside search service from our server, without anything that identifies you.') })
        Bullet({ text: tr('Inni użytkownicy nie widzą, kto dodał zgłoszenie albo głos.',
          'Other users do not see who added a report or a vote.') })
      }
      .margin({ top: 8 })
      SubTitle({ text: tr('To demo', 'This is a demo') })
      MessageBox({
        text: tr('Demo i wszystkie jego dane zostaną usunięte 4 października 2026, po ogłoszeniu wyników.',
          'The demo and all its data will be deleted on 4 October 2026, after the results are announced.'),
        kind: BoxKind.INFO
      }).margin({ top: 8 })
    }
  }
}

/** V-13: o danych, statusach i stanach odcinków. */
@Component
export struct AboutView {
  nav: Nav = new Nav();

  @Builder
  status(s: FactStatus, text: string) {
    Row({ space: 8 }) {
      Row().width(8).height(1.8).backgroundColor(P().text).margin({ top: 9 })
      Icon({ name: statusIcon(s), iconSize: 15, color: statusColor(s) }).margin({ top: 3 })
      Text() {
        Span(statusLabel(s)).fontFamily(FONT_B).fontColor(statusColor(s))
        Span(`: ${text}`).fontFamily(FONT).fontColor(P().text)
      }
      .fontSize(fs(14))
      .lineHeight(fs(20))
      .layoutWeight(1)
    }
    .width('100%')
    .alignItems(VerticalAlign.Top)
  }

  build() {
    PageBox() {
      BackLink({ action: () => this.nav.back() })
      PageTitle({
        title: tr('O danych', 'About the data'),
        intro: tr('Skąd wiemy o barierach i udogodnieniach i na ile można temu ufać.',
          'How we know about barriers and amenities and how far you can trust it.')
      })
      SubTitle({ text: tr('Skąd są informacje', 'Where the information comes from') })
      Column({ space: 8 }) {
        Bullet({ lead: 'OpenStreetMap.', text: tr(`Korzystamy z kopii danych z dnia ${formatDate(appModel.info().osmDate)}. Przy każdym takim fakcie podajemy datę jego ostatniej edycji w OpenStreetMap.`,
          `We use a copy of the data from ${formatDate(appModel.info().osmDate)}. For each such fact we show the date of its last edit in OpenStreetMap.`) })
        Bullet({ lead: tr('Zgłoszenia ludzi.', 'Reports from people.'),
          text: tr('Każdy może zgłosić barierę, udogodnienie albo obszar. Przy zgłoszeniu podajemy datę ostatniego potwierdzenia.',
            'Anyone can report a barrier, an amenity or an area. For a report we show the date of the last confirmation.') })
      }
      .margin({ top: 8 })
      SubTitle({ text: tr('Co znaczą statusy', 'What the statuses mean') })
      Column({ space: 8 }) {
        this.status(FactStatus.UNVERIFIED, tr('nikt jeszcze tego nie potwierdził albo potwierdzeń jest za mało.',
          'nobody has confirmed it yet, or there are too few confirmations.'))
        this.status(FactStatus.CONFIRMED, tr('inne osoby potwierdziły, że to nadal tu jest.',
          'other people confirmed that it is still there.'))
        this.status(FactStatus.DISPUTED, tr('jedne osoby potwierdzają, inne zgłaszają, że tego już nie ma.',
          'some people confirm it, others report that it is gone.'))
      }
      .margin({ top: 8 })
      Text(tr('Status nie zmienia się sam z upływem czasu. Datę widzisz przy każdym fakcie i oceniasz ją samodzielnie.',
        'A status does not change by itself over time. You see the date at every fact and judge it yourself.'))
        .fontFamily(FONT).fontSize(fs(14)).fontColor(P().text).lineHeight(fs(20)).margin({ top: 8 })
      SubTitle({ text: tr('Co znaczą odcinki trasy', 'What the route segments mean') })
      Column({ space: 8 }) {
        Bullet({ lead: tr('Bariera z potrzeb.', 'Barrier from your needs.'),
          text: tr('Na odcinku jest bariera, której unikasz.', 'The segment has a barrier you avoid.') })
        Bullet({ lead: tr('Bez barier, dane pełne.', 'No barriers, full data.'),
          text: tr('Znamy wszystko, co ważne dla Twoich potrzeb, i żadna z tych rzeczy nie jest barierą.',
            'We know everything that matters for your needs, and none of it is a barrier.') })
        Bullet({ lead: tr('Dane niepełne.', 'Incomplete data.'),
          text: tr('To, co wiemy, nie jest barierą, ale części informacji brakuje.',
            'What we know is not a barrier, but some information is missing.') })
        Bullet({ lead: tr('Brak danych.', 'No data.'),
          text: tr('Nie wiemy o odcinku nic, co ważne dla Twoich potrzeb.', 'We know nothing about the segment that matters for your needs.') })
      }
      .margin({ top: 8 })
      MessageBox({ text: tr('Brak informacji nigdy nie oznacza u nas, że miejsce jest dostępne.',
        'Missing information never means a place is accessible.'), kind: BoxKind.ERROR }).margin({ top: 10 })
      SubTitle({ text: tr('Dane przykładowe', 'Sample data') })
      Row({ space: 6 }) {
        Text(tr('W okolicy Tauron Areny dodaliśmy zgłoszenia i obszary na potrzeby pokazu. Każde ma znak',
          'Around Tauron Arena we added reports and areas for the demo. Each has the mark'))
          .fontFamily(FONT).fontSize(fs(14)).fontColor(P().text).layoutWeight(1)
      }
      .margin({ top: 6 })
      SampleChip().margin({ top: 6 })
      SubTitle({ text: tr('Jak poprawić błąd', 'How to fix a mistake') })
      Text(tr('Otwórz fakt i odpowiedz, czy nadal jest, albo dodaj własne zgłoszenie. Zapisanego zgłoszenia nikt nie edytuje.',
        'Open the fact and answer whether it is still there, or add your own report. Nobody edits a saved report.'))
        .fontFamily(FONT).fontSize(fs(14)).fontColor(P().text).lineHeight(fs(20)).margin({ top: 6 })
      SubTitle({ text: tr('Licencja mapy', 'Map licence') })
      Text(tr('Mapa i dane: © OpenStreetMap contributors, licencja ODbL.',
        'Map and data: © OpenStreetMap contributors, ODbL licence.'))
        .fontFamily(FONT).fontSize(fs(14)).fontColor(P().text).margin({ top: 6 })
    }
  }
}
