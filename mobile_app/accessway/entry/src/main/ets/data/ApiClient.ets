import { common } from '@kit.AbilityKit';
import { http } from '@kit.NetworkKit';
import { tr } from '../model/I18n';
import { ApiSettings, DEFAULT_TIMEOUT_MS } from './ApiConfig';
import { ApiErrorBody } from './ApiTypes';
import { ErrorCode, RepoError } from './Repository';
import { readFileText, removeFile, writeFileText } from './Storage';

const TOKEN_FILE: string = 'api_session_token.txt';

/** Whether a call sends the session token: never, if present, or always (then no token is a client-side error). */
export enum Auth {
  NONE = 'none',
  OPTIONAL = 'optional',
  REQUIRED = 'required'
}

export class ApiResponse {
  status: number = 0;
  body: string = '';
}

function headerValue(headers: Object, name: string): string {
  const rec = headers as Record<string, string | string[]>;
  for (const k of Object.keys(rec)) {
    if (k.toLowerCase() === name.toLowerCase()) {
      const v = rec[k];
      return Array.isArray(v) ? (v as string[])[0] ?? '' : `${v}`;
    }
  }
  return '';
}

/** Message for an error code from the contract, in the current language. */
export function apiErrorText(code: string, fields: string[]): string {
  if (code === 'routing_unavailable') {
    return tr('Usługa wyznaczania tras nie odpowiada. Nie pokazujemy trasy zgadywanej. Spróbuj ponownie za chwilę.',
      'The routing service does not answer. We do not show a guessed route. Try again in a moment.');
  }
  if (code === 'address_search_unavailable') {
    return tr('Wyszukiwarka adresów teraz nie odpowiada. Spróbuj ponownie za chwilę albo wskaż punkt na mapie.',
      'The address search does not answer right now. Try again in a moment or pick a point on the map.');
  }
  if (code === 'service_unavailable') {
    return tr('Serwer teraz nie odpowiada. Spróbuj ponownie za chwilę.', 'The server does not answer right now. Try again in a moment.');
  }
  if (code === 'invalid_search_text') {
    return tr('Wpisz adres albo nazwę miejsca, najwyżej 200 znaków.', 'Type an address or a place name, at most 200 characters.');
  }
  if (code === 'session_expired') {
    return tr('Sesja wygasła i zostałeś wylogowany. Zaloguj się i powtórz czynność.',
      'Your session expired and you were signed out. Sign in and repeat the action.');
  }
  if (code === 'authentication_required') {
    return tr('Ta czynność wymaga zalogowania.', 'This action needs you to sign in.');
  }
  if (code === 'invalid_credentials') {
    return tr('Pseudonim i hasło do siebie nie pasują. Sprawdź oba i spróbuj ponownie.',
      'The nickname and password do not match. Check both and try again.');
  }
  if (code === 'pseudonym_taken') {
    return tr('Ten pseudonim jest już zajęty. Wybierz inny.', 'This nickname is already taken. Choose another one.');
  }
  if (code === 'vote_too_soon') {
    return tr('Kolejny głos na ten fakt będzie możliwy po upływie doby.', 'You can vote on this fact again after a day.');
  }
  if (code === 'fact_not_found') {
    return tr('Tego faktu już nie ma albo został ukryty.', 'This fact no longer exists or was hidden.');
  }
  if (code === 'fact_not_flaggable') {
    return tr('Faktów z OpenStreetMap nie zgłasza się do moderacji.', 'Facts from OpenStreetMap cannot be sent to moderation.');
  }
  if (code === 'fact_not_flagged') {
    return tr('Ukryć można tylko treść zgłoszoną do moderacji.', 'Only flagged content can be hidden.');
  }
  if (code === 'moderator_role_required') {
    return tr('To konto nie ma roli moderatora.', 'This account is not a moderator.');
  }
  if (code === 'idempotency_key_reused') {
    return tr('To zgłoszenie zostało już zapisane z inną treścią.', 'This report was already saved with different content.');
  }
  if (code === 'invalid_request') {
    return tr(`Serwer odrzucił dane (${fields.join(', ')}).`, `The server refused the data (${fields.join(', ')}).`);
  }
  return tr('Serwer zgłosił błąd. Spróbuj ponownie za chwilę.', 'The server reported an error. Try again in a moment.');
}

function codeOf(apiCode: string, fields: string[]): ErrorCode {
  if (apiCode === 'routing_unavailable' || apiCode === 'address_search_unavailable' || apiCode === 'service_unavailable') {
    return ErrorCode.UNAVAILABLE;
  }
  if (apiCode === 'session_expired') {
    return ErrorCode.SESSION_EXPIRED;
  }
  if (apiCode === 'authentication_required') {
    return ErrorCode.AUTH_REQUIRED;
  }
  if (apiCode === 'invalid_credentials') {
    return ErrorCode.BAD_CREDENTIALS;
  }
  if (apiCode === 'pseudonym_taken') {
    return ErrorCode.TAKEN;
  }
  if (apiCode === 'vote_too_soon') {
    return ErrorCode.VOTE_TOO_SOON;
  }
  if (apiCode === 'fact_not_found' || apiCode === 'not_found') {
    return ErrorCode.NOT_FOUND;
  }
  if (apiCode === 'fact_not_flaggable' || apiCode === 'fact_not_flagged') {
    return ErrorCode.NOT_FLAGGABLE;
  }
  if (apiCode === 'moderator_role_required') {
    return ErrorCode.FORBIDDEN;
  }
  if (apiCode === 'invalid_request') {
    if (fields.indexOf('pseudonym') >= 0) {
      return ErrorCode.INVALID_PSEUDONYM;
    }
    if (fields.indexOf('password') >= 0) {
      return ErrorCode.INVALID_PASSWORD;
    }
    return ErrorCode.INVALID_REQUEST;
  }
  return ErrorCode.INTERNAL;
}

/**
 * HTTP client that follows the contract conventions: JSON in UTF-8, paths with the `/api` prefix, token in
 * `Authorization: Bearer`, renewed token from the `Session-Token` header saved on the device, errors as
 * `{ "error": { "code": ... } }` turned into a RepoError with a message for the person.
 */
export class ApiClient {
  settings: ApiSettings;
  private ctx: common.Context;
  private token: string = '';

  constructor(ctx: common.Context, settings: ApiSettings) {
    this.ctx = ctx;
    this.settings = settings;
    this.token = (readFileText(this.tokenPath()) ?? '').trim();
  }

  private tokenPath(): string {
    return `${this.ctx.filesDir}/${TOKEN_FILE}`;
  }

  hasToken(): boolean {
    return this.token.length > 0;
  }

  setToken(t: string): void {
    this.token = t.trim();
    if (this.token.length > 0) {
      writeFileText(this.tokenPath(), this.token);
    } else {
      removeFile(this.tokenPath());
    }
  }

  clearToken(): void {
    this.setToken('');
  }

  private method(m: string): http.RequestMethod {
    if (m === 'POST') {
      return http.RequestMethod.POST;
    }
    if (m === 'DELETE') {
      return http.RequestMethod.DELETE;
    }
    return http.RequestMethod.GET;
  }

  /** Sends the request and returns a 2xx response; turns any other into a RepoError. */
  async send(m: string, path: string, body: string, auth: Auth): Promise<ApiResponse> {
    if (auth === Auth.REQUIRED && !this.hasToken()) {
      throw new RepoError(ErrorCode.AUTH_REQUIRED, apiErrorText('authentication_required', []));
    }
    const headers: Record<string, string> = { 'Accept': 'application/json' };
    if (body.length > 0) {
      headers['Content-Type'] = 'application/json';
    }
    const sentToken = auth !== Auth.NONE && this.hasToken();
    if (sentToken) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    const req = http.createHttp();
    const out = new ApiResponse();
    try {
      const options: http.HttpRequestOptions = {
        method: this.method(m),
        header: headers,
        expectDataType: http.HttpDataType.STRING,
        connectTimeout: this.settings.timeout_ms ?? DEFAULT_TIMEOUT_MS,
        readTimeout: this.settings.timeout_ms ?? DEFAULT_TIMEOUT_MS
      };
      if (body.length > 0) {
        options.extraData = body;
      }
      const res = await req.request(`${this.settings.base_url}${path}`, options);
      out.status = res.responseCode;
      out.body = typeof res.result === 'string' ? res.result as string : '';
      const renewed = headerValue(res.header, 'Session-Token');
      if (renewed.length > 0 && (sentToken || path === '/api/sessions')) {
        this.setToken(renewed);
      }
    } catch (e) {
      throw new RepoError(ErrorCode.UNAVAILABLE, tr('Brak połączenia z serwerem. Sprawdź internet i spróbuj ponownie.',
        'No connection to the server. Check the internet and try again.'));
    } finally {
      req.destroy();
    }
    if (out.status >= 200 && out.status < 300) {
      return out;
    }
    let apiCode = '';
    let fields: string[] = [];
    try {
      const err = JSON.parse(out.body) as ApiErrorBody;
      apiCode = err.error.code;
      fields = err.error.fields ?? [];
    } catch (e) {
      apiCode = out.status === 503 ? 'service_unavailable' : 'internal_error';
    }
    if (apiCode === 'session_expired') {
      this.clearToken();
    }
    throw new RepoError(codeOf(apiCode, fields), apiErrorText(apiCode, fields));
  }
}
