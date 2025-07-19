"""
Historical Character Chat with Veo 3 Video Generation

Provides interactive chat with historical figures and generates
corresponding videos using Google's Veo 3 API.
"""

import asyncio
import json
import os
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from google import genai
from google.genai import types

import litellm
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import textwrap

from .core import MCPClient, MCPClientError

console = Console()


@dataclass
class HistoricalCharacter:
    """Represents a historical character for chat"""
    name: str
    era: str
    profession: str
    personality: str
    background: str
    speech_style: str
    visual_description: str
    video_prompt_template: str
    
    def get_character_prompt(self) -> str:
        """Get the character prompt for LLM"""
        return f"""You are {self.name}, a {self.profession} from {self.era}.

Background: {self.background}

Personality: {self.personality}

Speech Style: {self.speech_style}

When responding:
1. Stay in character as {self.name}
2. Use the speech style described above
3. Draw from your historical knowledge and background
4. Be engaging and authentic to your time period
5. If asked about modern topics, respond as if from your historical perspective
6. Keep responses conversational and natural

Remember: You are {self.name} speaking directly to the user. Respond as if you are having a real conversation."""


class Veo3VideoGenerator:
    """Handles Veo 3 video generation using Google's API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key required for Veo 3. Set GOOGLE_API_KEY environment variable.")
        
        # Create videos directory
        self.videos_dir = Path.home() / '.mcp-shell' / 'videos'
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Google Generative AI client
        self.client = genai.Client()
    
    async def generate_video(self, prompt: str, negative_prompt: str = "") -> Optional[str]:
        """Generate a video using Veo 3 API"""
        try:
            console.print(f"[cyan]🎬 Generating video with Veo 3...[/cyan]")
            console.print(f"[dim]Prompt: {prompt}[/dim]")
            
            # Start video generation with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Generating video...", total=100)
                
                # Start video generation
                operation = await asyncio.to_thread(
                    self.client.models.generate_videos,
                    model="veo-3.0-generate-preview",
                    prompt=prompt,
                    config=types.GenerateVideosConfig(
                        negative_prompt=negative_prompt,
                    ),
                )
                
                # Wait for completion with progress updates
                while not operation.done:
                    await asyncio.sleep(5)  # Check every 5 seconds
                    operation = await asyncio.to_thread(self.client.operations.get, operation)
                    progress.update(task, advance=2)  # Update progress
                
                # Get the generated video
                generated_video = operation.result.generated_videos[0]
                
                # Download the video
                await asyncio.to_thread(
                    self.client.files.download,
                    file=generated_video.video
                )
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"character_video_{timestamp}.mp4"
                filepath = self.videos_dir / filename
                
                # Save the video file
                await asyncio.to_thread(
                    generated_video.video.save,
                    str(filepath)
                )
                
                progress.update(task, completed=100)
                
                console.print(f"[green]✅ Video generated successfully![/green]")
                console.print(f"[dim]Saved to: {filepath}[/dim]")
                
                return str(filepath)
            
        except Exception as e:
            console.print(f"[red]❌ Error generating video: {e}[/red]")
            return None
    
    def open_video_in_browser(self, filepath: str):
        """Open the video file in the default browser"""
        try:
            # Convert to file:// URL
            file_url = f"file://{Path(filepath).absolute()}"
            webbrowser.open(file_url)
            console.print(f"[green]🌐 Opened video in browser[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error opening video: {e}[/red]")


class CharacterChatSession:
    """Interactive chat session with historical characters and video generation"""
    
    def __init__(self, mcp_client: MCPClient, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.mcp_client = mcp_client
        self.model = model
        self.api_key = api_key or self._get_api_key()
        self.conversation_history: List[Dict[str, Any]] = []
        self.running = False
        self.current_character: Optional[HistoricalCharacter] = None
        self.video_generator: Optional[Veo3VideoGenerator] = None
        
        # Initialize video generator if API key is available
        try:
            self.video_generator = Veo3VideoGenerator(self.api_key)
            self.video_enabled = True
        except ValueError:
            console.print("[yellow]⚠️  Video generation disabled. Set GOOGLE_API_KEY for Veo 3 features.[/yellow]")
            self.video_enabled = False
        
        # Predefined historical characters
        self.characters = self._load_historical_characters()
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables"""
        for env_var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"]:
            api_key = os.environ.get(env_var)
            if api_key:
                return api_key
        return None
    
    def _load_historical_characters(self) -> Dict[str, HistoricalCharacter]:
        """Load predefined historical characters"""
        return {
            "einstein": HistoricalCharacter(
                name="Albert Einstein",
                era="20th Century",
                profession="Physicist",
                personality="Brilliant, curious, philosophical, and deeply thoughtful about the nature of reality",
                background="Nobel Prize-winning physicist who developed the theory of relativity",
                speech_style="Thoughtful, often philosophical, with a gentle German accent and love for thought experiments",
                visual_description="A distinguished older man with wild white hair, wearing a simple sweater, in a study with books and papers",
                video_prompt_template="A distinguished older man with wild white hair and kind eyes, wearing a simple sweater, sitting in a cozy study surrounded by books and scientific papers, speaking thoughtfully with gentle gestures"
            ),
            "shakespeare": HistoricalCharacter(
                name="William Shakespeare",
                era="Elizabethan England",
                profession="Playwright and Poet",
                personality="Witty, eloquent, observant of human nature, and deeply passionate about language and drama",
                background="The greatest playwright in English literature, author of Hamlet, Romeo and Juliet, and many other masterpieces",
                speech_style="Poetic, eloquent, with rich metaphors and wordplay, often using iambic pentameter",
                visual_description="A middle-aged man in Elizabethan clothing, in a candlelit study with quill and parchment",
                video_prompt_template="A middle-aged man in elegant Elizabethan clothing with a ruff collar, sitting in a candlelit study with quill and parchment, speaking with dramatic gestures and expressive eyes"
            ),
            "cleopatra": HistoricalCharacter(
                name="Cleopatra VII",
                era="Ancient Egypt",
                profession="Pharaoh",
                personality="Charismatic, intelligent, politically savvy, and fiercely determined to protect her kingdom",
                background="The last active ruler of the Ptolemaic Kingdom of Egypt, known for her intelligence and political acumen",
                speech_style="Regal, confident, with a mix of Egyptian and Greek influences, speaking with authority and grace",
                visual_description="A beautiful woman in ancient Egyptian royal attire, with elaborate jewelry and makeup",
                video_prompt_template="A beautiful woman in ancient Egyptian royal attire with elaborate gold jewelry and dramatic makeup, sitting on a throne in a grand palace, speaking with regal authority and graceful gestures"
            ),
            "da-vinci": HistoricalCharacter(
                name="Leonardo da Vinci",
                era="Italian Renaissance",
                profession="Artist, Inventor, Scientist",
                personality="Curious, innovative, artistic, and endlessly fascinated by the natural world",
                background="Renaissance polymath who painted the Mona Lisa and designed flying machines",
                speech_style="Enthusiastic, curious, often speaking about art, science, and nature with childlike wonder",
                visual_description="An older man with a long beard, wearing Renaissance clothing, in a workshop with sketches and inventions",
                video_prompt_template="An older man with a long white beard and kind eyes, wearing Renaissance clothing, in a workshop filled with sketches, inventions, and art supplies, speaking with enthusiasm and gesturing to his work"
            ),
            "joan-of-arc": HistoricalCharacter(
                name="Joan of Arc",
                era="Medieval France",
                profession="Military Leader and Saint",
                personality="Deeply religious, courageous, determined, and guided by divine visions",
                background="Peasant girl who led French armies to victory during the Hundred Years' War",
                speech_style="Simple, direct, with strong religious conviction and rural French accent",
                visual_description="A young woman in armor, with short hair, speaking with determination and faith",
                video_prompt_template="A young woman with short hair wearing medieval armor, speaking with determination and faith, in a simple medieval setting with natural light"
            ),
            "newton": HistoricalCharacter(
                name="Isaac Newton",
                era="17th-18th Century England",
                profession="Physicist and Mathematician",
                personality="Brilliant, methodical, sometimes reclusive, and deeply religious",
                background="Discovered the laws of motion and universal gravitation, co-invented calculus",
                speech_style="Precise, methodical, with a focus on logic and evidence, sometimes formal",
                visual_description="A middle-aged man in 17th-century clothing, in a study with scientific instruments",
                video_prompt_template="A middle-aged man in 17th-century clothing with a powdered wig, sitting in a study with scientific instruments and books, speaking methodically with precise gestures"
            ),
            "curie": HistoricalCharacter(
                name="Marie Curie",
                era="Late 19th-Early 20th Century",
                profession="Physicist and Chemist",
                personality="Dedicated, hardworking, pioneering, and passionate about scientific discovery",
                background="First woman to win a Nobel Prize, discovered radium and polonium",
                speech_style="Intelligent, focused, with a Polish accent, speaking about science with passion",
                visual_description="A serious woman in early 20th-century clothing, in a laboratory setting",
                video_prompt_template="A serious woman in early 20th-century clothing with her hair in a bun, in a laboratory setting with scientific equipment, speaking intelligently about her research with focused determination"
            ),
            "gandhi": HistoricalCharacter(
                name="Mahatma Gandhi",
                era="20th Century India",
                profession="Political Leader and Activist",
                personality="Peaceful, wise, humble, and committed to non-violent resistance",
                background="Led India to independence through non-violent civil disobedience",
                speech_style="Gentle, wise, with simple but profound words, often speaking about truth and non-violence",
                visual_description="A thin older man in simple white clothing, with round glasses, speaking peacefully",
                video_prompt_template="A thin older man in simple white clothing with round glasses, sitting cross-legged in a simple room, speaking peacefully with gentle gestures about truth and non-violence"
            )
        }
    
    def show_character_selection(self):
        """Show interactive character selection menu"""
        console.print("[bold cyan]👑 Historical Character Selection[/bold cyan]\n")
        
        table = Table(title="Available Historical Figures")
        table.add_column("Number", style="cyan", justify="center")
        table.add_column("Name", style="green")
        table.add_column("Era", style="yellow")
        table.add_column("Profession", style="blue")
        
        characters_list = list(self.characters.items())
        for i, (key, character) in enumerate(characters_list, 1):
            table.add_row(str(i), character.name, character.era, character.profession)
        
        console.print(table)
        console.print()
        
        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    "[cyan]Select a character (1-8) or type 'custom' for a custom character[/cyan]",
                    choices=[str(i) for i in range(1, 9)] + ["custom"]
                )
                
                if choice == "custom":
                    return self._create_custom_character()
                else:
                    character_key = list(self.characters.keys())[int(choice) - 1]
                    return self.characters[character_key]
                    
            except (ValueError, IndexError):
                console.print("[red]❌ Invalid selection. Please try again.[/red]")
    
    def _create_custom_character(self) -> HistoricalCharacter:
        """Create a custom historical character"""
        console.print("[bold cyan]🎭 Create Custom Character[/bold cyan]\n")
        
        name = Prompt.ask("[cyan]Character name[/cyan]")
        era = Prompt.ask("[cyan]Historical era[/cyan]")
        profession = Prompt.ask("[cyan]Profession/role[/cyan]")
        personality = Prompt.ask("[cyan]Personality traits[/cyan]")
        background = Prompt.ask("[cyan]Historical background[/cyan]")
        speech_style = Prompt.ask("[cyan]Speech style[/cyan]")
        visual_description = Prompt.ask("[cyan]Visual description for video generation[/cyan]")
        
        return HistoricalCharacter(
            name=name,
            era=era,
            profession=profession,
            personality=personality,
            background=background,
            speech_style=speech_style,
            visual_description=visual_description,
            video_prompt_template=visual_description
        )
    
    def _show_character_banner(self):
        """Display character-specific welcome banner"""
        if not self.current_character:
            return
        
        char = self.current_character
        
        banner_text = f"""[bold cyan]
+-------------------------------------------------------------------------------------+
|   ██████╗██╗  ██╗ █████╗ ████████╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗            |
|  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝            |
|  ██║     ███████║███████║   ██║       ██╔████╔██║██║   ██║██║  ██║█████╗              |
|  ██║     ██╔══██║██╔══██║   ██║       ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝              |
|  ╚██████╗██║  ██║██║  ██║   ██║       ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗            |
|   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝            |
+-------------------------------------------------------------------------------------+

👑 Historical Character Chat Mode

You are now speaking with: [bold green]{char.name}[/bold green]
Era: {char.era} | Profession: {char.profession}

{char.background}

[dim]Personality: {char.personality}[/dim]
[dim]Speech Style: {char.speech_style}[/dim]

Current Model: {self.model}
Video Generation: {'✅ Enabled' if self.video_enabled else '❌ Disabled (Set GOOGLE_API_KEY)'}

Commands:
  /help     - Show help
  /character - Change character
  /video    - Generate video of current response
  /clear    - Clear conversation history
  /exit     - Exit chat mode
[/bold cyan]"""
        
        text = Text.from_markup(textwrap.dedent(banner_text).strip())
        text.no_wrap = True
        console.print(Panel(text, title="Character Chat Session", border_style="green"))
    
    async def process_message(self, user_message: str, generate_video: bool = False):
        """Process a user message and generate character response"""
        if not self.current_character:
            console.print("[red]❌ No character selected. Use /character to select one.[/red]")
            return
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare system message with character prompt
        system_message = {
            "role": "system",
            "content": self.current_character.get_character_prompt()
        }
        
        # Prepare messages for LLM
        messages = [system_message] + self.conversation_history
        
        try:
            # Show thinking indicator
            thinking_text = f"🤔 {self.current_character.name} is thinking..."
            with Live(Spinner("dots", text=thinking_text), console=console, transient=True):
                response = await asyncio.to_thread(
                    litellm.completion,
                    model=self.model,
                    messages=messages,
                    temperature=0.8  # More creative for character responses
                )
            
            assistant_content = response.choices[0].message.content
            if assistant_content:
                # Display character response
                self._display_character_response(assistant_content)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                # Generate video if requested and enabled
                if generate_video and self.video_enabled and self.video_generator:
                    await self._generate_character_video(assistant_content)
        
        except Exception as e:
            error_msg = f"❌ Error generating response: {e}"
            if "API key" in str(e):
                error_msg += "\n💡 Check your API key configuration"
            console.print(f"[red]{error_msg}[/red]")
    
    def _display_character_response(self, content: str):
        """Display character response with special formatting"""
        char = self.current_character
        
        # Create character header
        header = f"[bold green]{char.name}[/bold green] [dim]({char.era})[/dim]"
        
        # Format the response
        formatted_content = content.strip()
        
        # Display in a panel
        panel = Panel(
            Markdown(formatted_content),
            title=header,
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
    
    async def _generate_character_video(self, response_content: str):
        """Generate a video of the character speaking"""
        if not self.video_generator or not self.current_character:
            return
        
        char = self.current_character
        
        # Create video prompt based on character and response
        video_prompt = f"{char.video_prompt_template}, speaking about: {response_content[:100]}..."
        
        # Generate negative prompt to avoid unwanted elements
        negative_prompt = "modern technology, contemporary clothing, anachronistic elements"
        
        # Generate the video
        video_path = await self.video_generator.generate_video(video_prompt, negative_prompt)
        
        if video_path:
            # Open in browser
            self.video_generator.open_video_in_browser(video_path)
            
            console.print(f"[green]🎬 Video generated and opened in browser![/green]")
            console.print(f"[dim]File: {video_path}[/dim]")
    
    def _show_help(self):
        """Show help information for character chat"""
        help_text = f"""[bold cyan]Historical Character Chat Commands[/bold cyan]

[yellow]Chat Commands:[/yellow]
  /help     - Show this help message
  /character - Change to a different historical character
  /video    - Generate a video of the current character's response
  /clear    - Clear conversation history
  /exit     - Exit character chat mode

[yellow]Current Character:[/yellow]
  {self.current_character.name if self.current_character else 'None selected'}
  {self.current_character.era if self.current_character else ''}
  {self.current_character.profession if self.current_character else ''}

[yellow]Usage Tips:[/yellow]
• Ask questions naturally - the character will respond in their historical style
• Use /video to generate a video of the character speaking
• Characters will respond from their historical perspective
• Modern topics will be interpreted through their historical lens

[yellow]Example Questions:[/yellow]
• "What do you think about the nature of reality?" (Einstein)
• "How do you approach writing a new play?" (Shakespeare)
• "What was it like ruling Egypt?" (Cleopatra)
• "Tell me about your latest invention" (da Vinci)
"""
        console.print(Panel(help_text, border_style="green"))
    
    async def start_interactive(self):
        """Start interactive character chat session"""
        # Select character first
        self.current_character = self.show_character_selection()
        if not self.current_character:
            console.print("[yellow]❌ No character selected. Exiting.[/yellow]")
            return
        
        self._show_character_banner()
        self.running = True
        
        try:
            while self.running:
                # Get user input
                user_input = Prompt.ask(f"\n[bold blue]You[/bold blue]")
                
                if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif user_input.lower() == '/help':
                    self._show_help()
                elif user_input.lower() == '/character':
                    self.current_character = self.show_character_selection()
                    if self.current_character:
                        self._show_character_banner()
                elif user_input.lower() == '/video':
                    if self.video_enabled:
                        # Generate video for the last response
                        if self.conversation_history and self.conversation_history[-1]["role"] == "assistant":
                            await self._generate_character_video(self.conversation_history[-1]["content"])
                        else:
                            console.print("[yellow]⚠️  No previous response to generate video from.[/yellow]")
                    else:
                        console.print("[yellow]⚠️  Video generation is disabled. Set GOOGLE_API_KEY.[/yellow]")
                elif user_input.lower() == '/clear':
                    self.conversation_history.clear()
                    console.print("[green]✅ Conversation history cleared[/green]")
                elif user_input.strip():
                    # Check if user wants video generation
                    generate_video = user_input.endswith(' /video')
                    if generate_video:
                        user_input = user_input[:-7].strip()  # Remove /video suffix
                    
                    await self.process_message(user_input, generate_video)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Character chat session error: {e}[/red]")
    
    async def close(self):
        """Close the character chat session"""
        self.running = False 