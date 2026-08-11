import type { AskResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class FriendlyError extends Error {}

export async function askQuestion(question: string): Promise<AskResponse> {
  let res: Response
  try {
    res = await fetch(`${API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })
  } catch {
    throw new FriendlyError(
      "We couldn't reach the server. Check your connection and try again.",
    )
  }

  if (!res.ok) {
    throw new FriendlyError(
      'Something went wrong on our end while answering that question. Please try again.',
    )
  }

  const data = (await res.json()) as AskResponse

  if (data.error && !data.sql) {
    throw new FriendlyError(
      "We couldn't turn that into a data query. Try rephrasing your question, " +
        'or use one of the example questions below.',
    )
  }

  return data
}
