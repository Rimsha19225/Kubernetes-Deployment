# Floating Chatbot Component

A floating AI chatbot component for the Todo Web Application that provides an always-accessible chat interface.

## Features

- Fixed position floating button at bottom-right corner
- Headset icon with pulsing animation to indicate interactivity
- Smooth slide-up animation when opened
- Responsive design for mobile and desktop
- Integration with existing Tailwind theme (purple/pink gradient)
- Auto-scrolling to latest messages
- Typing indicators for bot responses
- Clean, modern UI matching application theme

## Usage

The component is integrated globally in the root layout (`src/app/layout.tsx`) and is available throughout the entire application.

```tsx
<FloatingChatbot />
```

## Props

The component doesn't accept any props as it's designed to be a standalone global component.

## Styling

- Uses the application's primary color scheme: gradients from purple (#6B46C1) to pink (#EC4899)
- Responsive design with max-width constraints
- Smooth transitions and animations
- Shadow effects and rounded corners for modern UI

## State Management

- `isOpen`: Controls the visibility of the chat panel
- `messages`: Array of chat messages with sender type and timestamps
- `inputValue`: Current value of the message input field
- `isTyping`: Shows typing indicator when bot is "thinking"

## Accessibility

- Proper ARIA labels for interactive elements
- Keyboard navigation support (Enter to send message)
- Sufficient contrast for readability
- Focus management for modal interactions