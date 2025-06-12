import type { Meta, StoryObj } from '@storybook/react'
import App from './App'

const meta = {
  title: 'MarkView/App',
  component: App,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'MarkView メインアプリケーション - リアルタイムMarkdownプレビューエディタ'
      }
    }
  },
  tags: ['autodocs'],
} satisfies Meta<typeof App>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: 'デフォルト表示',
  parameters: {
    docs: {
      description: {
        story: 'デフォルトのMarkdownコンテンツが表示された状態のアプリケーション'
      }
    }
  }
}

export const EmptyEditor: Story = {
  name: '空のエディタ',
  parameters: {
    docs: {
      description: {
        story: 'エディタが空の状態（実際の実装では初期値があるため参考用）'
      }
    }
  }
} 