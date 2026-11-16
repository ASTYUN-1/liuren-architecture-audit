import type { InterviewFileItem, InterviewListItem } from './types';
interface DashboardInterviewItem extends InterviewListItem {
    url: string;
    mode: string;
    resumeSlug: string;
    sessionID?: string;
    directory?: string;
}
export declare function renderDashboardPage(interviews: DashboardInterviewItem[], files: InterviewFileItem[], outputFolder: string): string;
export declare function renderInterviewPage(interviewId: string, resumeSlug: string): string;
export {};
