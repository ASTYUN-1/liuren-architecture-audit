import { z } from 'zod';
import { type PluginConfig } from '../config/schema';
export type DoctorArgs = {
    json?: boolean;
    error?: string;
    help?: boolean;
};
export declare function parseDoctorArgs(args: string[]): DoctorArgs;
export type ConfigCheckResult = {
    scope: 'user' | 'project';
    path: string | null;
    exists: boolean;
    ok: boolean;
    config?: PluginConfig;
    error?: {
        kind: 'invalid-json' | 'invalid-schema' | 'read-error';
        message: string;
        issues?: z.ZodIssue[];
    };
};
export type PresetCheckResult = {
    preset: string;
    ok: boolean;
    error?: {
        kind: 'missing-preset';
        message: string;
    };
};
export type DoctorResult = {
    ok: boolean;
    project: string;
    configs: ConfigCheckResult[];
    presetCheck?: PresetCheckResult;
};
export declare function runDoctorCheck(cwd: string): DoctorResult;
export declare function formatHumanDoctorResult(result: DoctorResult): string;
export declare function formatJsonDoctorResult(result: DoctorResult): string;
export declare function doctor(args: DoctorArgs): Promise<number>;
