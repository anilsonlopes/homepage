import { event } from 'vue-gtag';

export function trackEvent(name, parameters = {}) {
  if (!import.meta.env.PROD) return;

  event(name, parameters);
}
