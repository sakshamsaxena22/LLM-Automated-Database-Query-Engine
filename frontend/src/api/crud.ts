import apiClient from './client';
import type { CrudListParams, CrudListResponse, CrudCreateRequest, CrudUpdateRequest, Document } from '@/types/crud';

export const crudApi = {
  list: async (params: CrudListParams): Promise<CrudListResponse> => {
    const { collection, ...queryParams } = params;
    const { data } = await apiClient.get<CrudListResponse>(`/crud/${collection}`, {
      params: queryParams,
    });
    return data;
  },

  get: async (collection: string, id: string): Promise<Document> => {
    const { data } = await apiClient.get<Document>(`/crud/${collection}/${id}`);
    return data;
  },

  create: async (payload: CrudCreateRequest): Promise<Document> => {
    const { collection, document } = payload;
    const { data } = await apiClient.post<Document>(`/crud/${collection}`, document);
    return data;
  },

  update: async (payload: CrudUpdateRequest): Promise<Document> => {
    const { collection, id, update } = payload;
    const { data } = await apiClient.put<Document>(`/crud/${collection}/${id}`, update);
    return data;
  },

  delete: async (collection: string, id: string): Promise<void> => {
    await apiClient.delete(`/crud/${collection}/${id}`);
  },

  getCollections: async (): Promise<string[]> => {
    const { data } = await apiClient.get<string[]>('/crud/collections');
    return data;
  },
};
