"""
Clean text formatter for Discovery Reports
Converts markdown to beautifully formatted plain text with proper spacing
"""

import re
from textwrap import fill, indent


class DiscoveryReportFormatter:
    """Format discovery report markdown into clean, readable text output."""
    
    def __init__(self, line_width: int = 80):
        self.line_width = line_width
        self.output_lines = []
    
    def format(self, markdown_content: str) -> str:
        """Convert markdown content to formatted text."""
        self.output_lines = []
        
        lines = markdown_content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            # H1 headers
            if line.startswith('# '):
                self._flush_section(current_section, section_content)
                title = line[2:].strip()
                self._add_title(title)
                current_section = 'title'
                section_content = []
            
            # H2 headers (sections)
            elif line.startswith('## '):
                self._flush_section(current_section, section_content)
                section_title = line[3:].strip()
                self._add_section_header(section_title)
                current_section = 'body'
                section_content = []
            
            # Regular content
            else:
                if current_section:
                    section_content.append(line)
        
        # Flush final section
        self._flush_section(current_section, section_content)
        
        return '\n'.join(self.output_lines)
    
    def _flush_section(self, section_type: str, content: list) -> None:
        """Process and add accumulated section content."""
        if not content or not section_type:
            return
        
        text = '\n'.join(content).strip()
        if not text:
            return
        
        # Process different section types
        self._process_content(text)
    
    def _process_content(self, text: str) -> None:
        """Process and format content blocks."""
        blocks = self._split_blocks(text)
        
        for block_type, content in blocks:
            if block_type == 'paragraph':
                self._add_paragraph(content)
            elif block_type == 'bullet':
                self._add_bullet(content)
            elif block_type == 'numbered':
                self._add_numbered_item(content)
            elif block_type == 'table':
                self._add_table(content)
            elif block_type == 'code':
                self._add_code_block(content)
    
    def _split_blocks(self, text: str) -> list:
        """Split text into blocks (paragraphs, lists, tables, etc)."""
        blocks = []
        current_block = []
        current_type = None
        
        lines = text.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # Empty line - flush current block
            if not stripped:
                if current_block and current_type:
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                current_block = []
                current_type = None
                continue
            
            # Bullet point
            if re.match(r'^[-*•]\s+', stripped):
                if current_type and current_type != 'bullet':
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                    current_block = []
                current_type = 'bullet'
                current_block.append(stripped)
            
            # Numbered list
            elif re.match(r'^\d+[.)]\s+', stripped):
                if current_type and current_type != 'numbered':
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                    current_block = []
                current_type = 'numbered'
                current_block.append(stripped)
            
            # Table row
            elif '|' in stripped:
                if current_type and current_type != 'table':
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                    current_block = []
                current_type = 'table'
                current_block.append(stripped)
            
            # Code block
            elif stripped.startswith('```'):
                if current_type and current_type != 'code':
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                    current_block = []
                current_type = 'code'
                current_block.append(stripped)
            
            # Regular paragraph
            else:
                if current_type and current_type != 'paragraph':
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append((current_type, block_content))
                    current_block = []
                current_type = 'paragraph'
                current_block.append(line)
        
        # Flush final block
        if current_block and current_type:
            block_content = '\n'.join(current_block).strip()
            if block_content:
                blocks.append((current_type, block_content))
        
        return blocks
    
    def _add_title(self, text: str) -> None:
        """Add main title with formatting."""
        self.output_lines.append('')
        self.output_lines.append('═' * self.line_width)
        self.output_lines.append(text.center(self.line_width))
        self.output_lines.append('═' * self.line_width)
        self.output_lines.append('')
    
    def _add_section_header(self, text: str) -> None:
        """Add section header with formatting."""
        self.output_lines.append('')
        self.output_lines.append('─' * self.line_width)
        self.output_lines.append(f'► {text.upper()}')
        self.output_lines.append('─' * self.line_width)
        self.output_lines.append('')
    
    def _add_paragraph(self, text: str) -> None:
        """Add wrapped paragraph with proper spacing."""
        # Clean up markdown formatting
        text = self._clean_markdown(text)
        
        # Wrap text to line width
        wrapped = fill(text, width=self.line_width - 4, 
                      subsequent_indent='    ',
                      break_long_words=False,
                      break_on_hyphens=False)
        
        self.output_lines.append(wrapped)
        self.output_lines.append('')
    
    def _add_bullet(self, text: str) -> None:
        """Add bullet point with proper formatting."""
        text = self._clean_markdown(text)
        lines = text.split('\n')
        
        for line in lines:
            stripped = line.strip()
            # Remove existing bullet markers
            stripped = re.sub(r'^[-*•]\s+', '', stripped)
            
            # Wrap with indent
            wrapped = fill(stripped, width=self.line_width - 6,
                          initial_indent='  • ',
                          subsequent_indent='    ',
                          break_long_words=False,
                          break_on_hyphens=False)
            
            self.output_lines.append(wrapped)
        
        self.output_lines.append('')
    
    def _add_numbered_item(self, text: str) -> None:
        """Add numbered item with proper formatting."""
        text = self._clean_markdown(text)
        lines = text.split('\n')
        
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Remove existing number markers
            stripped = re.sub(r'^\d+[.)]\s+', '', stripped)
            
            # Wrap with indent
            wrapped = fill(stripped, width=self.line_width - 6,
                          initial_indent=f'  {idx}. ',
                          subsequent_indent='     ',
                          break_long_words=False,
                          break_on_hyphens=False)
            
            self.output_lines.append(wrapped)
        
        self.output_lines.append('')
    
    def _add_table(self, text: str) -> None:
        """Add formatted table."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Simple table formatting
        self.output_lines.append('')
        for line in lines:
            if '|' in line:
                # Clean up table syntax
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells:
                    self.output_lines.append('  ' + ' | '.join(cells))
        self.output_lines.append('')
    
    def _add_code_block(self, text: str) -> None:
        """Add code block with formatting."""
        lines = [l for l in text.split('\n') if l.strip() and not l.strip().startswith('```')]
        
        self.output_lines.append('')
        self.output_lines.append('  ┌' + '─' * (self.line_width - 4) + '┐')
        for line in lines:
            self.output_lines.append('  │ ' + line[:self.line_width-6].ljust(self.line_width - 6) + ' │')
        self.output_lines.append('  └' + '─' * (self.line_width - 4) + '┘')
        self.output_lines.append('')
    
    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting."""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Code
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Links
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        # HTML tags
        text = re.sub(r'<.+?>', '', text)
        
        return text.strip()


def format_discovery_report(markdown_content: str, line_width: int = 90) -> str:
    """
    Format a discovery report markdown content into clean, readable text.
    
    Args:
        markdown_content: The markdown content of the discovery report
        line_width: Width of output lines (default: 90)
    
    Returns:
        Formatted text string suitable for console or file output
    """
    formatter = DiscoveryReportFormatter(line_width=line_width)
    return formatter.format(markdown_content)
