import { VirtualConsole } from 'jsdom';
import { escapeHtml } from '../../utils/escape-html';
import { parseFrontmatter } from '../../utils/frontmatter';
import type { CachedFetch, ExtractedContent } from './types';
export { escapeHtml, parseFrontmatter };
/**
 * Suppresses css-tree lexer warnings ([csstree-match] prefix) emitted
 * synchronously during JSDOM construction (jsdom uses css-tree to parse
 * stylesheets; css-tree calls the global console.warn directly, bypassing
 * jsdom's virtualConsole). Other warnings pass through untouched.
 */
export declare function withCssTreeWarningsSuppressed<T>(fn: () => T): T;
/**
 * Suppresses jsdom "css-parsing" errors ("Could not parse CSS stylesheet")
 * that jsdom would otherwise forward to console.error when no custom
 * virtualConsole is supplied, leaking parser noise into the TUI. Other
 * jsdomErrors pass through to console.error as full error objects,
 * preserving stack, cause, and URL metadata.
 */
export declare function withJsdomCssParsingErrorsSuppressed<T>(fn: (vc: VirtualConsole) => T): T;
export declare function wordCount(text: string): number;
export declare function frontmatter(metadata: Record<string, unknown>): string;
export declare function trimBlankRuns(input: string): string;
export declare function cleanHeadingText(input: string): string;
export declare function cleanFetchedMarkdown(input: string): string;
export declare function cleanFetchedText(input: string): string;
export declare function withTruncationMarker(content: string, format: 'text' | 'markdown' | 'html', truncated: boolean): string;
export declare function joinRenderedContent(metadata: string, content: string, format: 'text' | 'markdown' | 'html'): string;
export declare function renderMessageForFormat(content: string, format: 'text' | 'markdown' | 'html'): string;
export declare function buildRedirectResultMessage(originalUrl: string, redirectUrl: string, statusCode: number): string;
export declare function buildLlmsRequiredMessage(originalUrl: string, reason?: string): string;
export declare function extractFromHtml(html: string, finalUrl: string, extractMain: boolean): Promise<ExtractedContent>;
export declare function inferCanonicalUrlFromText(content: string, finalUrl: string): string | undefined;
export declare function extractHeadingsFromMarkdown(content: string): string[] | undefined;
export declare function detectQualitySignals(fetchResult: Pick<CachedFetch, 'text' | 'markdown' | 'rawContent' | 'wordCount' | 'sourceKind' | 'extractedMain'>): string[];
export declare function pickContent(fetchResult: CachedFetch, format: 'text' | 'markdown' | 'html'): string;
