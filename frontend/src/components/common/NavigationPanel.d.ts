import { DefineComponent } from 'vue'

export interface NavigationItem {
  label: string;
  value: string;
  icon?: string;
  to?: string;
}

declare const NavigationPanel: DefineComponent<{
  items: NavigationItem[];
  mode?: 'vertical' | 'tabs';
  title?: string;
  initialItem?: string;
  drawerWidth?: number;
}>

export default NavigationPanel 