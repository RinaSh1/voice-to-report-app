import { getJson } from '../../lib/http'

export type Health = {
  status: string
  llm_provider: string
}

export const getHealth = () => getJson<Health>('/api/health')
