// export interface Version {
//   id: string;
//   versionNumber: number;
//   content: string;
//   createdAt: string;
//   sources?: Source[];
// }

// export interface StoredDocObject {
//   pmc_id: string;
//   title?: string;
//   filename?: string;
//   url: string;
//   createdAt: string;
// }

// export type StoredDocs = string | StoredDocObject;

// export interface Section {
//   heading: string;
//   paragraph: string;
//   sources?: Source[];
// }

// export interface StructuredContent {
//   title: string;
//   sections: Section[];
// }

// export interface Message {
//   id: string;
//   role: 'user' | 'assistant';
//   content: string | StructuredContent; 
//   sources?: Source[];
//   messageId?: number;
//   template?: string; 
//   imageUrl?: string;
//   createdAt: string;
// }

// export interface Source {
//   url: string;
//   page_no: number;
//   document_name: string;
// }

// export type FlexibleResponsePayload = {
//   user?: string;
//   assistant?: StructuredContent;
//   title?: string;
//   sections?: Section[];
// };

// export interface APIResponse {
//   session_id: string;
//   message_id: number;
//   response: FlexibleResponsePayload;
//   sources?: Source[];
//   selected_images?: string[]; 
//   images?: string[]; 
//   parameters: Record<string, string[]>;
//   selected_template?: string; 
//   template?: string;
// }

// export interface SessionHistoryData {
//   messages: Message[];
//   lastApiContext?: {
//       parameters?: Record<string, string[]>;
//       template?: string | null;
//       images?: (string | null)[];
//   };
// }

// export interface ValidationErrorDetail {
//   loc: (string | number)[];
//   msg: string;
//   type: string;
// }

// export interface ValidationError {
//   detail: ValidationErrorDetail[];
// }

// export interface ChatPayload {
//   session_id: string;
//   user_query: string | null;
//   images: string[];
//   parameters: Record<string, string[]>;
//   template: string;
//   message_id: number;
//   selectedImageUrl?: string | null;
//   selectedImageId?: string | null;
// }

export interface Version {
  id: string;
  versionNumber: number;
  content: string;
  createdAt: string;
  sources?: Source[];
}

export interface StoredDocObject {
  pmc_id: string;
  title?: string;
  filename?: string;
  url: string;
  createdAt: string;
}

export type StoredDocs = string | StoredDocObject;

export interface Section {
  heading: string;
  paragraph: string;
  sources?: Source[];
}

export interface StructuredContent {
  title: string;
  sections: Section[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string | StructuredContent; 
  sources?: Source[];
  messageId?: number;
  template?: string; 
  imageUrl?: string;
  createdAt: string;
}

export interface Source {
  url: string;
  page_no: number;
  document_name: string;
}

export type FlexibleResponsePayload = {
  user?: string;
  assistant?: StructuredContent;
  title?: string;
  sections?: Section[];
};

export interface APIResponse {
  session_id: string;
  message_id: number;
  response: FlexibleResponsePayload;
  qa_answer?: string;
  sources?: Source[];
  selected_images?: string[]; 
  images?: string[]; 
  parameters: Record<string, string[]>;
  selected_template?: string; 
  template?: string;
}

export interface SessionHistoryData {
  messages: Message[];
  lastApiContext?: {
      parameters?: Record<string, string[]>;
      template?: string | null;
      images?: (string | null)[];
  };
}

export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ValidationError {
  detail: ValidationErrorDetail[];
}

export interface ChatPayload {
  session_id: string;
  user_query: string | null;
  images: string[];
  parameters: Record<string, string[]>;
  template: string;
  message_id: number;
  selectedImageUrl?: string | null;
  selectedImageId?: string | null;
}