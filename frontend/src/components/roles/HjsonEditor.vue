<template>
  <div class="hjson-editor">
    <div class="ace-container" ref="aceContainer"></div>
    
    <div class="hjson-footer">
      <v-chip
        size="small"
        color="info"
        variant="outlined"
        class="mr-2"
      >
        HJSON Format
      </v-chip>
      <span class="text-caption text-medium-emphasis mr-2">
        Supports comments, unquoted keys and commas are optional
      </span>
      <v-tooltip location="top" max-width="400">
        <template v-slot:activator="{ props }">
          <v-btn
            size="x-small"
            icon="mdi-help-circle-outline"
            color="info"
            variant="text"
            v-bind="props"
            @click="showExampleDialog = true"
          />
        </template>
        <span>View example format</span>
      </v-tooltip>
    </div>
    
    <!-- Example Dialog -->
    <v-dialog v-model="showExampleDialog" max-width="600">
      <v-card>
        <v-card-title class="text-subtitle-1">
          HJSON Format Example
        </v-card-title>
        <v-card-text>
          <p class="text-caption mb-2">HJSON is a more human-friendly JSON format. You can:</p>
          <v-list density="compact" class="bg-grey-lighten-4 rounded mb-4">
            <v-list-item>
              <v-list-item-title>
                <code>// Add comments</code>
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <code>Write unquoted keys</code>
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <code>Skip commas</code>
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>
                <code>Use multiline strings</code>
              </v-list-item-title>
            </v-list-item>
          </v-list>
          
          <div class="example-wrapper">
            <pre class="hjson-example">
{
  // This is an example role tree with roots array
  roots: [
    {
      // First root role
      role: Product Manager
      description: Oversees product development
      subroles: [
        {
          role: UI/UX Designer
          description: Designs user interfaces
          subroles: []
        }
        {
          role: Feature Planner
          description: Plans new features
          subroles: []
        }
      ]
    }
    {
      // Second root role
      role: Engineering Lead
      description: Leads development team
      subroles: [
        {
          role: Frontend Developer
          description: Builds UI components
          subroles: []
        }
        {
          role: Backend Developer
          description: Implements API and services
          subroles: []
        }
      ]
    }
  ]
}
            </pre>
          </div>
          
          <v-btn 
            color="primary" 
            block 
            variant="outlined" 
            class="mt-4"
            @click="applyExample"
          >
            Use This Example
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showExampleDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import Hjson from 'hjson'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/theme-katzenmilch'
import 'ace-builds/src-noconflict/mode-hjson'

// Configure ace to avoid Node.js dependencies
// This prevents issues with modules like 'os' being required in the browser
ace.config.set('basePath', '/node_modules/ace-builds/src-noconflict');
ace.config.set('modePath', '/node_modules/ace-builds/src-noconflict');
ace.config.set('themePath', '/node_modules/ace-builds/src-noconflict');

// Define component props
const props = defineProps<{
  modelValue: string; // JSON string
  errorMessages?: string;
  label?: string;
  rows?: number;
  loading?: boolean;
  placeholder?: string;
}>();

// Define emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'validate', value: string): void;
}>();

// Internal state
const hjsonContent = ref('');
const internalError = ref<string | null>(null);
const showExampleDialog = ref(false);
const aceContainer = ref<HTMLElement | null>(null);
let editor: ace.Ace.Editor | null = null;
let ignoreNextChange = false;

// Example HJSON content
const exampleHjson = `{
  // This is an example role tree with roots array
  roots: [
    {
      // First root role
      role: Product Manager
      description: Oversees product development
      subroles: [
        {
          role: UI/UX Designer
          description: Designs user interfaces
          subroles: []
        }
        {
          role: Feature Planner
          description: Plans new features
          subroles: []
        }
      ]
    }
    {
      // Second root role
      role: Engineering Lead
      description: Leads development team
      subroles: [
        {
          role: Frontend Developer
          description: Builds UI components
          subroles: []
        }
        {
          role: Backend Developer
          description: Implements API and services
          subroles: []
        }
      ]
    }
  ]
}`;

// Apply example to editor
function applyExample() {
  if (editor) {
    editor.setValue(exampleHjson, -1);
    handleEditorChange();
  }
  showExampleDialog.value = false;
}

// Computed error messages
const errorMessages = computed(() => {
  return props.errorMessages || internalError.value || '';
});

// Handle editor content changes
function handleEditorChange() {
  if (!editor || ignoreNextChange) return;
  
  const content = editor.getValue();
  hjsonContent.value = content;
  
  let jsonValue;
  let isValid = false;
  
  try {
    // Parse HJSON to object
    const obj = Hjson.parse(content);
    
    // Convert back to JSON string
    jsonValue = JSON.stringify(obj, null, 2);
    isValid = true;
    
    // Emit the JSON string only when valid
    // emit('update:modelValue', jsonValue);
    
    internalError.value = null;
    
    // Remove error marker if exists
    if (editor.session.getAnnotations().length > 0) {
      editor.session.clearAnnotations();
    }
  } catch (error: unknown) {
    console.warn('Failed to parse HJSON:', error);
    jsonValue = content; // Use raw content for validation
    
    if (error instanceof Error) {
      internalError.value = error.message || 'Invalid HJSON format';
      
      // Add error annotation
      const match = String(error.message).match(/line (\d+)/);
      if (match && match[1]) {
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
  }
  
  // Always emit validate once with the appropriate value
  emit('validate', jsonValue);
}

// Initialize the Ace editor
function initializeEditor() {
  if (!aceContainer.value) return;
  
  editor = ace.edit(aceContainer.value, {
    mode: 'ace/mode/hjson',
    theme: 'ace/theme/katzenmilch',
    fontSize: 14,
    showPrintMargin: false,
    showGutter: true,
    highlightActiveLine: true,
    wrap: true,
  });

  // Set initial content
  if (hjsonContent.value) {
    editor.setValue(hjsonContent.value, -1);
  }
  
  // Set placeholder text in comments if provided
  if (props.placeholder) {
    // Add placeholder as a comment at the top of the file
    const placeholderComment = `// ${props.placeholder}\n`;
    if (!hjsonContent.value) {
      editor.setValue(placeholderComment, 1);
    }
  }
  
  // Handle editor changes
  editor.on('change', handleEditorChange);
  
  // Apply label as a comment at the top if provided
  // if (props.label) {
  //   const session = editor.getSession();
  //   session.on('changeAnnotation', function() {
  //     const annotations = session.getAnnotations();
  //     for (let i = 0; i < annotations.length; i++) {
  //       if (annotations[i].text === 'Missing semicolon.') {
  //         annotations.splice(i, 1);
  //         i--;
  //       }
  //     }
  //     session.setAnnotations(annotations);
  //   });
  // }
}

// Convert JSON to HJSON when modelValue changes
watch(() => props.modelValue, (newValue: string) => {
  if (!newValue) {
    hjsonContent.value = '';
    if (editor) {
      ignoreNextChange = true;
      editor.setValue('', -1);
      ignoreNextChange = false;
    }
    return;
  }
  
  try {
    // Parse JSON string to object
    const jsonObj = JSON.parse(newValue);
    
    // Convert to HJSON without using os module
    const newHjsonContent = Hjson.stringify(jsonObj, { 
      space: 2, 
      bracesSameLine: true
    });
    
    // Only update if content is different to prevent recursion
    if (hjsonContent.value !== newHjsonContent) {
      hjsonContent.value = newHjsonContent;
      
      // Update editor content if needed
      if (editor && editor.getValue() !== newHjsonContent) {
        ignoreNextChange = true;
        editor.setValue(newHjsonContent, -1);
        ignoreNextChange = false;
      }
    }
    
    internalError.value = null;
  } catch (error: unknown) {
    console.error('Failed to parse JSON:', error);
    
    // Only update if content is different to prevent recursion
    if (hjsonContent.value !== newValue) {
      hjsonContent.value = newValue; // Keep as is if invalid
      
      // Update editor content
      if (editor) {
        ignoreNextChange = true;
        editor.setValue(newValue, -1);
        ignoreNextChange = false;
      }
    }
    
    internalError.value = 'Invalid JSON format';
  }
}, { immediate: true });

// Watch for error messages from parent
watch(() => props.errorMessages, (errorMessage: string | undefined) => {
  if (editor && errorMessage) {
    // Try to extract line number info
    const match = String(errorMessage).match(/line (\d+)/);
    if (match && match[1]) {
      const lineNumber = parseInt(match[1], 10) - 1;
      editor.session.setAnnotations([{
        row: lineNumber,
        column: 0,
        text: errorMessage,
        type: "error"
      }]);
    }
  } else if (editor) {
    editor.session.clearAnnotations();
  }
});

// Initialize
onMounted(() => {
  // Initial conversion
  if (props.modelValue) {
    try {
      const jsonObj = JSON.parse(props.modelValue);
      hjsonContent.value = Hjson.stringify(jsonObj, { 
        space: 2, 
        bracesSameLine: true
      });
    } catch (error: unknown) {
      hjsonContent.value = props.modelValue;
    }
  }
  
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
  height: 100%;
}

.ace-container {
  width: 100%;
  height: calc(100% - 30px); /* Subtract footer height */
  min-height: 300px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.23);
}

.hjson-footer {
  display: flex;
  align-items: center;
  margin-top: 4px;
  height: 26px;
}

.example-wrapper {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 8px;
  margin-top: 16px;
  overflow-x: auto;
}

.hjson-example {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  white-space: pre;
  color: #333;
  margin: 0;
}
</style> 