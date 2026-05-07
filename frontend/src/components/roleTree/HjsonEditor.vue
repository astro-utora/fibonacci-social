<template>
  <div class="hjson-editor">
    <div class="ace-container" ref="aceContainer"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed } from '@vue/runtime-core'
import Hjson from 'hjson'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/theme-katzenmilch'
import 'ace-builds/src-noconflict/mode-hjson'

// Configure ace to avoid Node.js dependencies
ace.config.set('basePath', '/node_modules/ace-builds/src-noconflict');
ace.config.set('modePath', '/node_modules/ace-builds/src-noconflict');
ace.config.set('themePath', '/node_modules/ace-builds/src-noconflict');

// Define component props
const props = defineProps({
  value: {
    type: [String, Number, Boolean, Object, Array, null],
    default: null
  }
});

// Define emits
const emit = defineEmits(['update:value']);

// Internal state
const hjsonContent = ref('');
const internalError = ref<string | null>(null);
const aceContainer = ref<HTMLElement | null>(null);
let editor: ace.Ace.Editor | null = null;
let ignoreNextChange = false;

// Handle editor content changes
function handleEditorChange() {
  if (!editor || ignoreNextChange) return;
  
  const rawContent = editor.getValue();
  hjsonContent.value = rawContent;
  
  try {
    // Check if content is empty or just whitespace
    if (!rawContent.trim()) {
      emit('update:value', {});
      return;
    }
    
    // Add brackets back for parsing if necessary
    let contentToParse = rawContent;
    if (!rawContent.trim().startsWith('{') && !rawContent.trim().startsWith('[')) {
      // Make sure each line has proper key-value format
      const lines = rawContent.split('\n').map(line => line.trim()).filter(line => line);
      
      // If any line doesn't have a colon and is not a comment, it might be invalid
      const hasInvalidLines = lines.some(line => {
        // Skip comments
        if (line.startsWith('//') || line.startsWith('#')) return false;
        // Skip lines ending with a colon (might be an object)
        if (line.endsWith(':')) return false;
        // Check if line has a key-value format (contains a colon not in quotes)
        return !line.includes(':');
      });
      
      if (hasInvalidLines) {
        // Try to fix common issues - add quotes to keys that might need them
        const fixedLines = lines.map(line => {
          // Skip if already valid
          if (line.startsWith('//') || line.startsWith('#') || line.includes(':')) {
            return line;
          }
          
          // Try to quote what looks like a value without a key
          if (!isNaN(Number(line.trim()))) {
            return `"value": ${line}`;
          }
          
          // Otherwise, treat as string value
          return `"value": "${line}"`;
        });
        
        contentToParse = `{${fixedLines.join(',\n')}}`;
      } else {
        contentToParse = `{${rawContent}}`;
      }
    }
    
    // Parse HJSON to object
    const obj = Hjson.parse(contentToParse);
    
    // Emit the parsed value
    emit('update:value', obj);
    
    internalError.value = null;
    
    // Remove error marker if exists
    if (editor.session.getAnnotations().length > 0) {
      editor.session.clearAnnotations();
    }
    
    // Adjust editor height based on content
    updateEditorHeight();
  } catch (error: unknown) {
    console.warn('Failed to parse HJSON:', error);
    
    if (error instanceof Error) {
      internalError.value = error.message || 'Invalid HJSON format';
      
      // Add error annotation
      const match = String(error.message).match(/line (\d+)/);
      if (match && match[1]) {
        // Adjust line number if we added wrapper brackets
        const lineNumber = parseInt(match[1], 10) - 1;
        editor.session.setAnnotations([{
          row: lineNumber,
          column: 0,
          text: error.message,
          type: "error"
        }]);
      }
    } else {
      internalError.value = 'Invalid HJSON format';
    }
    
    // Still update height even on error
    updateEditorHeight();
  }
}

// Update editor height based on content
function updateEditorHeight() {
  if (!editor || !aceContainer.value) return;
  
  // Get line count and set height accordingly with some padding
  const lineCount = editor.session.getLength();
  const lineHeight = editor.renderer.lineHeight;
  const minHeight = Math.max(3 * lineHeight, 60); // At least 3 lines or 60px
  const contentHeight = Math.max(minHeight, lineCount * lineHeight + 15); // +15px for padding
  
  aceContainer.value.style.height = `${contentHeight}px`;
  editor.resize();
}

// Initialize the Ace editor
function initializeEditor() {
  if (!aceContainer.value) return;
  
  editor = ace.edit(aceContainer.value, {
    mode: 'ace/mode/hjson',
    theme: 'ace/theme/katzenmilch',
    fontSize: 14,
    showPrintMargin: false,
    showGutter: false,
    highlightActiveLine: true,
    wrap: true,
    autoScrollEditorIntoView: true,
    maxLines: Infinity // Allow infinite lines for auto-height
  });

  // Handle editor changes
  editor.on('change', handleEditorChange);
  
  // Set initial content
  updateEditorContent();
  
  // Set up a timer to periodically check and update height
  // This helps with dynamic content changes
  setTimeout(() => {
    updateEditorHeight();
  }, 100);
}

// Update the editor content from props
function updateEditorContent() {
  if (!editor) return;
  
  let content = '';
  
  if (props.value === null) {
    content = 'null';
  } else if (typeof props.value === 'object') {
    // Stringify the object with HJSON
    content = Hjson.stringify(props.value, { 
      space: 2, 
      bracesSameLine: true
    });
    
    // Remove outer brackets and completely remove indentation
    const lines = content.split('\n');
    
    // Process the lines to remove indentation
    const processedLines = lines
      .map(line => line.trim()) // Remove all whitespace from beginning of each line
      .filter((line, index) => {
        // Skip the first and last line if they're just brackets
        if ((index === 0 && line === '{') || 
            (index === lines.length - 1 && line === '}')) {
          return false;
        }
        return true;
      });
    
    // Join the lines back together
    content = processedLines.join('\n');
    
    // Remove trailing commas that might exist in HJSON
    content = content.replace(/,\s*$/gm, '');
  } else {
    content = String(props.value);
  }
  
  ignoreNextChange = true;
  editor.setValue(content, -1);
  ignoreNextChange = false;
  
  // Update height after content change
  setTimeout(() => {
    updateEditorHeight();
  }, 10);
}

// Watch for value changes
watch(() => props.value, () => {
  updateEditorContent();
}, { deep: true });

// Initialize
onMounted(() => {
  // Initialize editor after DOM update
  setTimeout(() => {
    initializeEditor();
  }, 0);
});

// Clean up
onBeforeUnmount(() => {
  if (editor) {
    editor.destroy();
    editor = null;
  }
});
</script>

<style scoped>
.hjson-editor {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.ace-container {
  width: 100%;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.23);
  transition: height 0.1s ease;
  overflow: hidden;
}

.hjson-footer {
  display: flex;
  align-items: center;
  margin-top: 4px;
  height: 26px;
  font-size: 12px;
}
</style>