import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

describe('App', () => {
  it('アプリケーションのタイトルが表示される', () => {
    render(<App />)
    expect(screen.getByText('MarkView')).toBeInTheDocument()
  })

  it('デフォルトのMarkdownコンテンツが表示される', () => {
    render(<App />)
    expect(screen.getByText('MarkView へようこそ！')).toBeInTheDocument()
  })

  it('Markdownエディタが表示される', () => {
    render(<App />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeInTheDocument()
    expect(textarea).toHaveAttribute('placeholder', 'ここにMarkdownを入力してください...')
  })

  it('プレビューエリアが表示される', () => {
    render(<App />)
    expect(screen.getByText('プレビュー')).toBeInTheDocument()
  })

  it('HTMLコピーボタンが表示される', () => {
    render(<App />)
    expect(screen.getByText('HTMLをコピー')).toBeInTheDocument()
  })

  it('HTMLダウンロードボタンが表示される', () => {
    render(<App />)
    expect(screen.getByText('HTMLをダウンロード')).toBeInTheDocument()
  })

  it('ステータスバーに統計情報が表示される', () => {
    render(<App />)
    expect(screen.getByText(/文字数:/)).toBeInTheDocument()
    expect(screen.getByText(/単語数:/)).toBeInTheDocument()
    expect(screen.getByText(/最終更新:/)).toBeInTheDocument()
  })

  it('テキストエリアに入力すると統計情報が更新される', async () => {
    render(<App />)
    const textarea = screen.getByRole('textbox')
    
    fireEvent.change(textarea, { target: { value: 'Hello World' } })
    
    // 統計情報の更新を確認
    expect(screen.getByText(/文字数: 11/)).toBeInTheDocument()
    expect(screen.getByText(/単語数: 2/)).toBeInTheDocument()
  })
}) 