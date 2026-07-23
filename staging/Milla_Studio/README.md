<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Milla 3.0 - AI Virtual Assistant 🚀

An advanced AI virtual assistant powered by Google Gemini, featuring integrated development tools, creative studio, and intelligent collaboration capabilities.

View your app in AI Studio: https://ai.studio/apps/drive/19jqfQTMSapioINoNOHkP9bhI2hG3zx8U

---

## ✨ New in Version 3.0

### 🛠️ **Sandbox IDE**
- Full-featured integrated development environment
- Multi-file support (HTML, CSS, JavaScript, TypeScript)
- Live preview with console output
- GitHub repository integration
- AI-assisted code generation
- Real-time syntax validation
- Code formatting with Prettier

### 🎨 **Creative Studio**
- Professional image generation platform
- Dual AI models (Gemini 3 Pro Image & Imagen 3)
- Multiple aspect ratios (1:1, 16:9, 9:16, 3:4, 4:3)
- Image comparison mode
- Gallery management
- Set as wallpaper feature

### 💭 **Thought Logger**
- Real-time display of AI reasoning process
- Transparent decision-making
- Educational insights
- Collapsible interface

### 📺 **Screen Share**
- Capture and analyze user's screen
- Gemini Vision-powered analysis
- Debug UI/UX issues
- Visual problem-solving

### 🎭 **Adaptive Persona**
- Context-aware personality adjustment
- Automatic mode switching
- 6 persona modes including Adaptive
- Emotional intelligence

### 🌌 **Proactive Background Generation**
- Automatic ambient wallpaper creation
- Beautiful generative art every 10 minutes
- Non-intrusive design
- Customizable themes

---

## 🚀 Quick Start

**Prerequisites:**  Node.js

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set your Gemini API key:**
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Run the app:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   Navigate to `http://localhost:3000`

---

## 🎯 Features

### Core Capabilities
- 🧠 **Chat**: Advanced conversational AI with context understanding
- 🔍 **Search**: Web search powered by Google
- 🗺️ **Maps**: Location services and navigation
- 🖼️ **Imagine**: AI image generation
- 🎬 **Veo**: AI video generation
- 🎤 **Live Voice**: Real-time voice interaction

### Developer Tools
- 💻 **Code together** in the Sandbox IDE
- 🔗 **GitHub integration** for repository exploration
- 🤖 **AI code generation** and assistance
- 🐛 **Visual debugging** with screen share

### Creative Tools
- 🎨 **Generate art** with multiple AI models
- 🖼️ **Manage gallery** of creations
- 🔄 **Remix prompts** for iteration
- 🌈 **Dynamic backgrounds** for inspiration

### Intelligence
- 📊 **12-axis self-evaluation** metrics
- 🧠 **Recursive learning** from interactions
- 💾 **External memory database** with persistence
- 🎓 **Knowledge base** expansion
- ⚖️ **Ethical auditing** system

---

## 💡 Usage Examples

### Open the Sandbox
```
User: "open sandbox"
Milla: 🛠️ Sandbox IDE opened. Let's build something together!
```

### Generate Art
```
User: "open studio"
Milla: 🎨 Creative Studio opened. Let's create some art!
```

### Screen Assistance
```
User: [Clicks screen share icon]
Milla: 📺 I can see your screen. How can I help?
```

### Collaborate on Code
```
User: "Let's build a calculator"
Milla: [Opens Sandbox] Great! I'll start with the HTML structure...
```

---

## 🏗️ Project Structure

```
Milla2.0/
├── components/
│   ├── Avatar3D.tsx          # 3D avatar rendering
│   ├── Dashboard.tsx         # Metrics and controls
│   ├── Sandbox.tsx           # 🆕 IDE component
│   ├── CreativeStudio.tsx    # 🆕 Image generation
│   ├── ThoughtLogger.tsx     # 🆕 Reasoning display
│   ├── LiveSession.tsx       # Voice interaction
│   └── YouTubePlayer.tsx     # Video player
├── services/
│   ├── geminiService.ts      # AI integration
│   ├── memoryDatabase.ts     # Persistent storage
│   └── githubService.ts      # 🆕 GitHub API
├── types.ts                  # TypeScript definitions
├── constants.ts              # 🆕 Model constants
├── App.tsx                   # Main application
└── NEW_CAPABILITIES.md       # 🆕 Feature documentation
```

---

## 🧪 Testing

Run the integration test suite:
```bash
bash test-integration.sh
```

All 41 tests should pass ✅

---

## 📦 Dependencies

### Core
- React 19.2.1
- TypeScript 5.8.2
- Vite 6.2.0
- @google/genai 1.31.0

### UI & Graphics
- @react-three/fiber 9.4.2
- @react-three/drei 10.7.7
- three 0.181.2
- recharts 3.5.1

### Development Tools
- prettier (for code formatting)
- react-simple-code-editor (IDE component)
- prismjs (syntax highlighting)

---

## 🎨 Customization

### Persona Modes
- Professional: Formal and precise
- Casual: Friendly and relaxed
- Empathetic: Supportive and understanding
- Humorous: Light and entertaining
- Motivational: Encouraging and inspiring
- **Adaptive**: Automatically adjusts based on context

### Themes
Milla generates dynamic backgrounds with themes including:
- Cosmic nebulas
- Digital landscapes
- Gradient waves
- Geometric patterns
- Light particles

---

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_api_key_here
```

### GitHub Integration
For private repositories, add a Personal Access Token in the Sandbox UI.

### Memory Database
Stored in browser localStorage:
- `milla_messages`: Chat history
- `milla_kb`: Knowledge base
- `milla_sandbox_files`: Sandbox files
- `milla_creative_studio_images`: Generated images

---

## 📚 Documentation

- **NEW_CAPABILITIES.md**: Comprehensive guide to new features
- **GEMINI.md**: Original Gemini API documentation
- **MEMORY_DATABASE.md**: Memory system documentation

---

## 🤝 Contributing

Milla is designed for collaboration! Use the Sandbox to:
1. Prototype new features
2. Debug existing code
3. Experiment with AI integration
4. Build extensions

---

## 📄 License

Private project - All rights reserved

---

## 🎉 Get Started!

```bash
npm install
# Add your GEMINI_API_KEY to .env
npm run dev
# Visit http://localhost:3000
# Type: "open sandbox" or "open studio"
```

---

<div align="center">
<strong>Built with ❤️ using Google Gemini</strong>
<br />
<em>Your AI development partner, creative collaborator, and intelligent assistant</em>
</div>
