declare module 'hjson' {
  /**
   * Parse hjson string into an object
   */
  export function parse(text: string): any;

  /**
   * Stringify an object to hjson
   */
  export function stringify(
    value: any, 
    options?: {
      space?: number | string;
      bracesSameLine?: boolean;
      quotes?: 'always' | 'keys' | 'strings' | 'all' | string;
      multiline?: 'std' | 'no-tabs' | 'off' | string;
      separator?: boolean;
      comma?: boolean;
      emitRootBraces?: boolean;
    }
  ): string;

  /**
   * Endquotes the provided string if it contains //
   */
  export function endquote(text: string): string;

  /**
   * Remove comments from an object
   */
  export function removeComments(value: any): any;

  /**
   * Default export
   */
  const hjson: {
    parse: typeof parse;
    stringify: typeof stringify;
    endquote: typeof endquote;
    removeComments: typeof removeComments;
  };
  
  export default hjson;
} 