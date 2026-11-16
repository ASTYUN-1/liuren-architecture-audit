import { z } from 'zod';
import { type CouncillorModelEntry } from '../utils/councillor-models';
export type { CouncillorModelEntry };
/**
 * Configuration for a single councillor within a preset.
 * Each councillor is an independent LLM that processes the same prompt.
 *
 * Councillors run as agent sessions with read-only codebase access
 * (read, glob, grep, lsp, list). They can examine the codebase but
 * cannot modify files or spawn subagents.
 *
 * `model` accepts a single ID or an ordered fallback chain. The parsed config
 * exposes `models` (the normalized chain) plus `model` (the primary, for
 * backward compatibility).
 */
export declare const CouncillorConfigSchema: z.ZodPipe<z.ZodObject<{
    model: z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodUnion<readonly [z.ZodString, z.ZodObject<{
        id: z.ZodString;
        variant: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>]>>]>;
    variant: z.ZodOptional<z.ZodString>;
    prompt: z.ZodOptional<z.ZodString>;
}, z.core.$strip>, z.ZodTransform<{
    model: string;
    variant: string | undefined;
    prompt: string | undefined;
    models: CouncillorModelEntry[];
}, {
    model: string | (string | {
        id: string;
        variant?: string | undefined;
    })[];
    variant?: string | undefined;
    prompt?: string | undefined;
}>>;
export type CouncillorConfig = z.infer<typeof CouncillorConfigSchema>;
/**
 * A named preset grouping several councillors.
 *
 * All keys are treated as councillor names mapping to councillor configs.
 * The reserved key `"master"` is silently ignored (legacy from when
 * council-master was a separate agent).
 */
export declare const CouncilPresetSchema: z.ZodPipe<z.ZodRecord<z.ZodString, z.ZodRecord<z.ZodString, z.ZodUnknown>>, z.ZodTransform<Record<string, {
    model: string;
    variant: string | undefined;
    prompt: string | undefined;
    models: CouncillorModelEntry[];
}>, Record<string, Record<string, unknown>>>>;
export type CouncilPreset = z.infer<typeof CouncilPresetSchema>;
/**
 * Top-level council configuration.
 *
 * Example JSONC:
 * ```jsonc
 * {
 *   "council": {
 *     "presets": {
 *       "default": {
 *         "alpha": { "model": "openai/gpt-5.6-luna" },
 *         "beta":  { "model": "openai/gpt-5.3-codex" },
 *         "gamma": { "model": "google/gemini-3-pro" }
 *       }
 *     }
 *   }
 * }
 * ```
 */
export declare const CouncilConfigSchema: z.ZodPipe<z.ZodObject<{
    presets: z.ZodRecord<z.ZodString, z.ZodPipe<z.ZodRecord<z.ZodString, z.ZodRecord<z.ZodString, z.ZodUnknown>>, z.ZodTransform<Record<string, {
        model: string;
        variant: string | undefined;
        prompt: string | undefined;
        models: CouncillorModelEntry[];
    }>, Record<string, Record<string, unknown>>>>>;
    default_preset: z.ZodDefault<z.ZodString>;
}, z.core.$loose>, z.ZodTransform<{
    presets: Record<string, Record<string, {
        model: string;
        variant: string | undefined;
        prompt: string | undefined;
        models: CouncillorModelEntry[];
    }>>;
    default_preset: string;
    _deprecated: string[] | undefined;
}, {
    [x: string]: unknown;
    presets: Record<string, Record<string, {
        model: string;
        variant: string | undefined;
        prompt: string | undefined;
        models: CouncillorModelEntry[];
    }>>;
    default_preset: string;
}>>;
export type CouncilConfig = z.infer<typeof CouncilConfigSchema>;
