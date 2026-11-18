import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Remove what each test rendered, so tests never see each other's page.
afterEach(cleanup)
