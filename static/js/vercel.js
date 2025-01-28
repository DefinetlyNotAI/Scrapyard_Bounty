import { inject } from "@vercel/analytics"
import { injectSpeedInsights } from '@vercel/speed-insights';

injectSpeedInsights();
inject();
