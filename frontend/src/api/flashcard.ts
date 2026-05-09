import request from './request'

export interface Flashcard {
  id: number
  knowledge_point_id: number
  front: string
  back: string
  flashcard_type: string
  created_at: string
  updated_at: string
}

export interface FlashcardCreate {
  front: string
  back: string
  flashcard_type?: string
}

export interface FlashcardUpdate {
  front?: string
  back?: string
  flashcard_type?: string
}

export function getFlashcards(knowledgePointId: number) {
  return request.get(`/api/flashcards?knowledge_point_id=${knowledgePointId}`) as Promise<Flashcard[]>
}

export function createFlashcard(knowledgePointId: number, data: FlashcardCreate) {
  return request.post(`/api/flashcards?knowledge_point_id=${knowledgePointId}`, data) as Promise<Flashcard>
}

export function updateFlashcard(id: number, data: FlashcardUpdate) {
  return request.put(`/api/flashcards/${id}`, data) as Promise<Flashcard>
}

export function deleteFlashcard(id: number) {
  return request.delete(`/api/flashcards/${id}`) as Promise<{ success: boolean; message: string }>
}

export function generateFlashcards(knowledgePointId: number) {
  return request.post(`/api/flashcards/generate-from-point/${knowledgePointId}`) as Promise<{
    knowledge_point_id: number
    created_count: number
    skipped_count: number
    flashcards: Flashcard[]
  }>
}
