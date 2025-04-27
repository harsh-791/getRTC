export interface ExtractedInfo {
  'Survey Number': string;
  'Surnoc': string;
  'Hissa': string;
  'Village': string;
  'Hobli': string;
  'Taluk': string;
  'District': string;
}

export interface Screenshot {
  name: string;
  url: string;
}

export interface ProcessImageResponse {
  success: boolean;
  message: string;
  extracted_info: ExtractedInfo;
  scraping_result: any[];
  screenshots: Screenshot[];
  record_id: number;
}

export interface GetScreenshotsResponse {
  success: boolean;
  screenshots: Screenshot[];
}