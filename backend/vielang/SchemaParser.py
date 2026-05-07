import re
import logging
from pydantic import BaseModel
from typing import List, Tuple, Optional, Dict, Any
from vielang.StructuredCategory import (
    StructuredProject, StructuredMorphism, StructuredMorphismType,
    StructuredEdge, Decomposition, Substitution, Product, Coproduct,
    StructuredProjectViewType
)

logger = logging.getLogger(__name__)

class SchemaParser:
    grammar = '''
Schema grammar:

Schema := FlowchartHeader NEWLINE StructuredProject*

FlowchartHeader := "flowchart TD" | "flowchart LR" | "flowchart RL" | "flowchart BT"

VertexDef := VertexID ["[\"" Content "\"]"]

Edge := ElementRef "-->" EdgeID ["[\"" Content "\"]"] ElementRef

ElementRef := VertexRef | EdgeRef
VertexRef := VertexID ["[\"" Content "\"]"]
EdgeRef := EdgeID

VertexID := "v" NUMBER
EdgeID := "e" NUMBER
Content := STRING

StructuredProject := Composition | SingleStructuredProject

Composition := "composition" NEWLINE
               INDENT (SingleStructuredProject | Edge)+ DEDENT

SingleStructuredProject := Product | Coproduct | Substitution | Decomposition

Product := "product" Edge NEWLINE
           (INDENT "branch" NEWLINE
               INDENT (Edge | StructuredProject)+ DEDENT
           )+ DEDENT

Coproduct := "coproduct" Edge NEWLINE
             (INDENT "branch" NEWLINE
                 INDENT (Edge | StructuredProject)+ DEDENT
             )+ DEDENT

Substitution := "substitution" Edge NEWLINE
                INDENT (Edge | StructuredProject)+ DEDENT

Decomposition := "decomposition" Edge NEWLINE
                 INDENT (Edge | StructuredProject)+ DEDENT

NUMBER := DIGIT+
DIGIT := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
STRING := Any text that may include escaped quotes (\")
INDENT := Increased indentation level (typically spaces or tabs)
DEDENT := Return to previous indentation level
NEWLINE := Line break character
    '''

    grammar_example_schema = '''flowchart TD
    product v3 -->e6["Product Operation"] v5
        branch
            v3 -->e7["Path 1"] v5
        branch
            v3 -->e8["Path 2"] v5

    composition
        substitution v1 -->e9["Complex Flow"] v5
            v1 -->e10["Initial"] v11
            decomposition v11 -->e12["Process"] v13
                v11 -->e14["Step 1"] v15
                v15 -->e16["Step 2"] v13
            v13 -->e17["Final"] v5'''

    # Pattern to match text content that can contain escaped quotes and empty strings
    quoted_text = r'(?:[^"\\]|\\"|\\)*?'  # Make it non-greedy with ? and allow empty string
    
    # Pattern for element ID (can be vertex v{number} or edge e{number})
    element_id = r'[ve]\d+'
    
    # Pattern for a stand-alone vertex definition: v1["Content"]
    standalone_vertex_pattern = re.compile(fr'(v\d+)\["({quoted_text})"\](?!\s*-->)', re.DOTALL)
    
    # Pattern for a full edge statement: v1["Content"] -->e2["Content"] v3["Content"] or e1 -->e2["Content"] v3
    full_edge_pattern = re.compile(
        fr'({element_id})(?:\["({quoted_text})"\])?\s+-->(e\d+)\["({quoted_text})"\]\s+({element_id})(?:\["({quoted_text})"\])?', 
        re.DOTALL
    )
    
    # Pattern for structured project start
    composition_pattern = re.compile(r'composition\s*\n', re.DOTALL)
    structured_project_pattern = re.compile(r'(product|coproduct|substitution|decomposition)\s+', re.DOTALL)
    branch_pattern = re.compile(r'branch\s*\n', re.DOTALL)
    
    # Patterns for whitespace and indentation
    newline_pattern = re.compile(r'\n')
    whitespace_pattern = re.compile(r'\s+')

    class Vertex(BaseModel):
        id: int
        content: str
    
    class Edge(BaseModel):
        id: int
        source_id: int
        target_id: int
        content: str

    @staticmethod
    def parse_schema_elements(schema: str, strict: bool = True) -> tuple[list[StructuredProject], dict[int, str]]:
        """Parse a flowchart schema back into lists of vertices, edges, and structured projects.
        
        Args:
            schema: The flowchart schema string
            
        Returns:
            A list of StructuredProject objects
        """
        # Remove the flowchart header
        content = schema.replace("flowchart TD", "").replace("flowchart LR", "").replace("flowchart RL", "").replace("flowchart BT", "")
        
        vertex_index: dict[int, str] = {}
        structured_projects = []
                
        # NEW APPROACH - Process the whole content with regex
        current_pos = 0
        while current_pos < len(content):
            # Skip whitespace at the beginning of line or between elements
            ws_match = SchemaParser.whitespace_pattern.match(content, current_pos)
            if ws_match:
                current_pos = ws_match.end()
                continue
                        
            # Try to match composition
            composition_match = SchemaParser.composition_pattern.match(content, current_pos)
            if composition_match:
                # Find the start position after the composition keyword
                start_pos = composition_match.end()

                current_indent = SchemaParser._get_indentation(content, current_pos)

                # Parse structured project text using recursive approach
                project, end_pos = SchemaParser._parse_structured_project_body_text(
                    content, vertex_index, start_pos, current_indent, StructuredMorphismType.Project, None
                )
                
                structured_projects.append(project)
                current_pos = end_pos
                continue
            
            # Try to match structured project (product, coproduct, substitution, decomposition)
            project_match = SchemaParser.structured_project_pattern.match(content, current_pos)
            if project_match:
                project_type = project_match.group(1)
                morphism_type = SchemaParser._get_morphism_type(project_type)
                
                # Find the edge that follows the project type keyword
                start_pos = project_match.end()
                edge_match = SchemaParser.full_edge_pattern.match(content, start_pos)
                
                if edge_match:
                    current_indent = SchemaParser._get_indentation(content, current_pos)
                    
                    # Extract the edge and move position past it
                    edge_text = edge_match.group(0)
                    start_pos = edge_match.end()
                    
                    # Parse the rest of the structured project
                    morphism, end_pos = SchemaParser._parse_structured_project_body_text(
                        content, vertex_index, start_pos, current_indent, morphism_type, edge_text
                    )
                    
                    project = StructuredProject(
                        id=morphism.id,
                        sourceId=morphism.sourceId,
                        targetId=morphism.targetId,
                        content=morphism.content,
                        type=morphism.type,
                        morphisms=[morphism],
                        viewType=StructuredProjectViewType.Full
                    )
                    structured_projects.append(project)
                    current_pos = end_pos
                    continue
            
            # Skip unmatched character
            message = f"Unmatched character at position {current_pos}: {content[current_pos:current_pos+40]}..."
            if strict:
                raise ValueError(message)
            else:
                logger.warning(message)
            current_pos += 1
        
        return structured_projects, vertex_index

    @staticmethod
    def _get_indentation(content: str, pos: int) -> int:
        """Calculate the indentation level at the given position in the content.
        
        Args:
            content: The content string
            pos: The position to calculate indentation for
            
        Returns:
            The indentation level (number of spaces)
        """
        # Find the beginning of the line containing pos
        line_start = content.rfind('\n', 0, pos)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1  # Move past the newline
        
        # Calculate indent (number of spaces at the beginning of the line)
        indent = 0
        current = line_start
        while current < len(content) and current < pos and content[current].isspace():
            indent += 1
            current += 1
        
        return indent

    @staticmethod
    def _get_next_line_indentation(content: str, pos: int) -> int:
        """Calculate the indentation of the next line after the given position.
        
        Args:
            content: The content string
            pos: The current position
            
        Returns:
            The indentation level of the next line (number of spaces)
        """
        # Find the next line after pos
        next_line_pos = content.find('\n', pos)
        if next_line_pos == -1:
            return 0  # No next line
            
        line_start = next_line_pos + 1  # Move past the newline
        
        # Find first non-whitespace character after the newline
        current = line_start
        while current < len(content) and content[current].isspace():
            current += 1
            
        return current - line_start

    @staticmethod
    def _parse_structured_project_body_text(
        content: str, 
        vertex_index: dict[int, str],
        start_pos: int, 
        parent_indent: int, 
        parent_type: StructuredMorphismType = StructuredMorphismType.Project,
        edge_text: str = None
    ) -> tuple[StructuredMorphism, int]:
        """Parse a structured project text starting at the given position.
        
        Args:
            content: The full content string
            start_pos: The starting position in the content
            parent_indent: The indentation level of the parent structured project
            parent_type: The type of the parent structured project
            edge_text: The edge text if the parent is not a Project
            
        Returns:
            A tuple of (structured_project, end_position)
        """
        
        print(f"_parse_structured_project_body_text parent_type: {parent_type}, parent_indent: {parent_indent}, edge_text: {edge_text}")
        # Generate a new ID for the project
        project_id = 1  # Will be properly set by category later
        
        # Create the base structured project based on parent_type
        if parent_type == StructuredMorphismType.Project:
            # For a regular StructuredProject
            project = StructuredProject(
                id=project_id,
                sourceId=0,  # Will be updated later
                targetId=0,  # Will be updated later
                content="",
                type=StructuredMorphismType.Project,
                morphisms=[],
                viewType=StructuredProjectViewType.Full
            )
        else:
            # Parse the edge text to get source and target IDs
            source_id, target_id, edge_content = 0, 0, ""
            if edge_text:
                edge, source_id, edge_id, target_id = SchemaParser.parse_edge(edge_text, vertex_index)
                edge_content = edge.content
            
            # Create the appropriate structured project type
            match parent_type:
                case StructuredMorphismType.Product:
                    project = Product(
                        id=project_id,
                        sourceId=source_id,
                        targetId=target_id,
                        content=edge_content,
                        subProjects=[]
                    )
                case StructuredMorphismType.Coproduct:
                    project = Coproduct(
                        id=project_id,
                        sourceId=source_id,
                        targetId=target_id,
                        content=edge_content,
                        subProjects=[]
                    )
                case StructuredMorphismType.Substitution:
                    sub_project = StructuredProject(
                        id=project_id + 1,
                        sourceId=source_id,
                        targetId=target_id,
                        content=None,
                        type=StructuredMorphismType.Project,
                        morphisms=[],
                        viewType=StructuredProjectViewType.Full
                    )
                    project = Substitution(
                        id=project_id,
                        sourceId=source_id,
                        targetId=target_id,
                        content=edge_content,
                        subProject=sub_project
                    )
                case StructuredMorphismType.Decomposition:
                    sub_project = StructuredProject(
                        id=project_id + 1,
                        sourceId=source_id,
                        targetId=target_id,
                        content=None,
                        type=StructuredMorphismType.Project,
                        morphisms=[],
                        viewType=StructuredProjectViewType.Full
                    )
                    project = Decomposition(
                        id=project_id,
                        sourceId=source_id,
                        targetId=target_id,
                        content=edge_content,
                        subProject=sub_project
                    )
        
        # Calculate initial indent level
        initial_indent = None
                
        # Start parsing project content
        current_pos = start_pos
        
        while current_pos < len(content):
            # Skip whitespace
            ws_match = SchemaParser.whitespace_pattern.match(content, current_pos)
            if ws_match:
                current_pos = ws_match.end()
                continue
            
            # Check for indentation change after a newline
            current_indent = SchemaParser._get_indentation(content, current_pos)
            print(f"_parse_structured_project_body_text current_indent: {current_indent}")
            if initial_indent is None:
                initial_indent = current_indent
                # Check that this project's indentation is greater than parent's indent (if parent_indent > 0)
                if initial_indent <= parent_indent:
                    logger.warning(f"Structured project at position {start_pos} has invalid indentation: {initial_indent} (should be > {parent_indent})")
                    return project, start_pos
            else:
                # If indent is less than the initial indent, we're done with this project
                if current_indent != initial_indent:
                    print(f"_parse_structured_project_body_text current_indent != initial_indent: {current_indent} != {initial_indent}")
                    prev_newline = content.rfind('\n', 0, current_pos)
                    return project, prev_newline
            
            # Check for branch in product/coproduct
            branch_match = SchemaParser.branch_pattern.match(content, current_pos)
            if branch_match:
                branch_start = branch_match.end()
                
                # Parse branch content recursively
                current_pos = branch_start

                branch_project, nested_end = SchemaParser._parse_structured_project_body_text(
                    content, vertex_index, current_pos, current_indent, StructuredMorphismType.Project, None
                )

                # Add the branch project to the appropriate container
                if parent_type in [StructuredMorphismType.Product, StructuredMorphismType.Coproduct]:
                    project.subProjects.append(branch_project)
                current_pos = nested_end
                continue
            
            # Check for nested structured project
            project_match = SchemaParser.structured_project_pattern.match(content, current_pos)
            if project_match:
                project_type = project_match.group(1)
                nested_type = SchemaParser._get_morphism_type(project_type)

                edge_match = SchemaParser.full_edge_pattern.match(content, project_match.end())
                if edge_match:
                    # Skip past the nested project definition
                    edge_text = edge_match.group(0)
                    current_pos = edge_match.end()
                   
                    # Parse the nested project using recursion with current indent as parent
                    nested_project, nested_end = SchemaParser._parse_structured_project_body_text(
                        content, vertex_index, current_pos, current_indent, nested_type, edge_text
                    )
                    
                    # Add the nested project to the appropriate container
                    if parent_type == StructuredMorphismType.Project:
                        project.morphisms.append(nested_project)
                    elif parent_type in [StructuredMorphismType.Substitution, StructuredMorphismType.Decomposition]:
                        project.subProject.morphisms.append(nested_project)
                    
                    current_pos = nested_end
                    continue
            
            # Check for edge
            edge_match = SchemaParser.full_edge_pattern.match(content, current_pos)
            if edge_match:
                # Parse the edge
                edge, source_id, edge_id, target_id = SchemaParser.parse_edge(edge_match.group(0), vertex_index)
                
                # Add the edge to the appropriate container
                if parent_type == StructuredMorphismType.Project:
                    project.morphisms.append(edge)
                elif parent_type in [StructuredMorphismType.Substitution, StructuredMorphismType.Decomposition]:
                    project.subProject.morphisms.append(edge)
                
                current_pos = edge_match.end()
                continue
            
            # If we reach end of content, we're done
            if current_pos >= len(content):
                break
                
            # If nothing matched, move to next character
            current_pos += 1
        
        # If we reached the end of content, return the project
        return project, current_pos

    @staticmethod
    def parse_vertex_ref(vertex_str: str) -> Tuple[int, str]:
        # Check if it's a vertex definition with content: v1["Content"]
        content_match = re.match(r'[ve](\d+)(?:\["([^"]*)"\])?', vertex_str)
        if not content_match:
            raise ValueError(f"Invalid vertex reference: {vertex_str}")
            
        vertex_id = int(content_match.group(1))
        if vertex_str.startswith("e"):
            vertex_id = -vertex_id
        content = content_match.group(2)
                    
        return vertex_id, content

    @staticmethod
    def parse_edge(edge_text: str, vertex_index: dict[int, str]) -> Tuple[StructuredEdge, int, int, int]:
        # Use a more robust pattern to match the edge structure with content
        # This handles quoted content in the edge more reliably
        pattern = r'([ve]\d+(?:\["[^"]*"\])?)\s+-->(e\d+)(?:\["([^"]*)"\])?\s+([ve]\d+(?:\["[^"]*"\])?)'
        match = re.match(pattern, edge_text)
        if not match:
            raise ValueError(f"Invalid edge format: {edge_text}")
        
        source_ref, edge_ref, edge_content, target_ref = match.groups()
        edge_content = edge_content or ""
        
        # Parse edge ID
        edge_id_match = re.match(r'e(\d+)', edge_ref)
        if not edge_id_match:
            raise ValueError(f"Invalid edge reference: {edge_ref}")
        edge_id = int(edge_id_match.group(1))
        
        # Parse source vertex
        source_id, source_content = SchemaParser.parse_vertex_ref(source_ref)
        vertex_index[source_id] = source_content
        
        # Parse target vertex
        target_id, target_content = SchemaParser.parse_vertex_ref(target_ref)
        vertex_index[target_id] = target_content
        
        # Create the edge morphism
        edge = StructuredEdge(
            id=edge_id,
            sourceId=source_id,
            targetId=target_id,
            content=edge_content
        )
                
        return edge, source_id, edge_id, target_id

    @staticmethod
    def _get_morphism_type(type_name: str) -> StructuredMorphismType:
        """Convert a type name string to a StructuredMorphismType enum value.
        
        Args:
            type_name: The type name string
            
        Returns:
            The corresponding StructuredMorphismType enum value
        """
        if type_name == "product":
            return StructuredMorphismType.Product
        elif type_name == "coproduct":
            return StructuredMorphismType.Coproduct
        elif type_name == "substitution":
            return StructuredMorphismType.Substitution
        elif type_name == "decomposition":
            return StructuredMorphismType.Decomposition
        else:
            return StructuredMorphismType.Project

    @staticmethod
    def parse_schema(schema: str, strict: bool = True) -> tuple[list[StructuredProject], dict[int, str]]:
        """Parse a flowchart schema into lists of StructuredProject objects.
        
        This method supports full grammar including vertices, edges, and structured projects.
        Vertices and edges can be defined together in a single line.
        
        Args:
            schema: The flowchart schema string
            strict: Whether to raise an error for unmatched text
            
        Returns:
            A list of StructuredProject objects
        """
        # Get the vertex, edge, and structured project strings
        structured_projects, vertex_index = SchemaParser.parse_schema_elements(schema, strict)        
        return structured_projects, vertex_index
