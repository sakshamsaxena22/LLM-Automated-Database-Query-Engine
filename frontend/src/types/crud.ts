export interface Collection {
  name: string;
  document_count: number;
  size_bytes: number;
  indexes: string[];
}

export interface Document {
  _id: string;
  [key: string]: unknown;
}

export interface CrudFilter {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains' | 'regex';
  value: string | number | boolean;
}

export interface CrudListParams {
  collection: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  filters?: CrudFilter[];
}

export interface CrudListResponse {
  data: Document[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface CrudCreateRequest {
  collection: string;
  document: Record<string, unknown>;
}

export interface CrudUpdateRequest {
  collection: string;
  id: string;
  update: Record<string, unknown>;
}
