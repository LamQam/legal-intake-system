// Auto-generated Supabase types based on our database schema
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: number
          email: string
          phone: string | null
          full_name: string
          role: 'client' | 'lawyer' | 'admin' | 'staff'
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          email: string
          phone?: string | null
          full_name: string
          role?: 'client' | 'lawyer' | 'admin' | 'staff'
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          email?: string
          phone?: string | null
          full_name?: string
          role?: 'client' | 'lawyer' | 'admin' | 'staff'
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      lawyers: {
        Row: {
          id: number
          user_id: number
          license_number: string | null
          specialization: string | null
          experience_years: number | null
          hourly_rate: number | null
          bio: string | null
          is_available: boolean
          rating: number
          total_cases: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          user_id: number
          license_number?: string | null
          specialization?: string | null
          experience_years?: number | null
          hourly_rate?: number | null
          bio?: string | null
          is_available?: boolean
          rating?: number
          total_cases?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          user_id?: number
          license_number?: string | null
          specialization?: string | null
          experience_years?: number | null
          hourly_rate?: number | null
          bio?: string | null
          is_available?: boolean
          rating?: number
          total_cases?: number
          created_at?: string
          updated_at?: string
        }
      }
      cases: {
        Row: {
          id: number
          case_number: string
          client_id: number
          lawyer_id: number | null
          title: string
          description: string | null
          case_type: string
          status: 'new' | 'in_progress' | 'pending_documents' | 'under_review' | 'closed' | 'cancelled'
          priority: 'low' | 'medium' | 'high' | 'urgent'
          jurisdiction: string | null
          estimated_value: number | null
          actual_value: number | null
          case_data: Json | null
          created_at: string
          updated_at: string
          closed_at: string | null
        }
        Insert: {
          id?: number
          case_number: string
          client_id: number
          lawyer_id?: number | null
          title: string
          description?: string | null
          case_type: string
          status?: 'new' | 'in_progress' | 'pending_documents' | 'under_review' | 'closed' | 'cancelled'
          priority?: 'low' | 'medium' | 'high' | 'urgent'
          jurisdiction?: string | null
          estimated_value?: number | null
          actual_value?: number | null
          case_data?: Json | null
          created_at?: string
          updated_at?: string
          closed_at?: string | null
        }
        Update: {
          id?: number
          case_number?: string
          client_id?: number
          lawyer_id?: number | null
          title?: string
          description?: string | null
          case_type?: string
          status?: 'new' | 'in_progress' | 'pending_documents' | 'under_review' | 'closed' | 'cancelled'
          priority?: 'low' | 'medium' | 'high' | 'urgent'
          jurisdiction?: string | null
          estimated_value?: number | null
          actual_value?: number | null
          case_data?: Json | null
          created_at?: string
          updated_at?: string
          closed_at?: string | null
        }
      }
      conversations: {
        Row: {
          id: number
          client_id: number
          phone_number: string
          status: 'new' | 'in_progress' | 'completed' | 'escalated'
          language: string
          current_stage: string
          conversation_data: Json | null
          whatsapp_message_id: string | null
          created_at: string
          updated_at: string
          completed_at: string | null
        }
        Insert: {
          id?: number
          client_id: number
          phone_number: string
          status?: 'new' | 'in_progress' | 'completed' | 'escalated'
          language?: string
          current_stage?: string
          conversation_data?: Json | null
          whatsapp_message_id?: string | null
          created_at?: string
          updated_at?: string
          completed_at?: string | null
        }
        Update: {
          id?: number
          client_id?: number
          phone_number?: string
          status?: 'new' | 'in_progress' | 'completed' | 'escalated'
          language?: string
          current_stage?: string
          conversation_data?: Json | null
          whatsapp_message_id?: string | null
          created_at?: string
          updated_at?: string
          completed_at?: string | null
        }
      }
      messages: {
        Row: {
          id: number
          conversation_id: number
          message_type: string
          content: string | null
          media_url: string | null
          media_type: string | null
          whatsapp_message_id: string | null
          is_from_user: boolean
          created_at: string
        }
        Insert: {
          id?: number
          conversation_id: number
          message_type?: string
          content?: string | null
          media_url?: string | null
          media_type?: string | null
          whatsapp_message_id?: string | null
          is_from_user?: boolean
          created_at?: string
        }
        Update: {
          id?: number
          conversation_id?: number
          message_type?: string
          content?: string | null
          media_url?: string | null
          media_type?: string | null
          whatsapp_message_id?: string | null
          is_from_user?: boolean
          created_at?: string
        }
      }
      documents: {
        Row: {
          id: number
          case_id: number
          name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          document_type: string | null
          is_confidential: boolean
          uploaded_by: number | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          case_id: number
          name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          document_type?: string | null
          is_confidential?: boolean
          uploaded_by?: number | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          case_id?: number
          name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          document_type?: string | null
          is_confidential?: boolean
          uploaded_by?: number | null
          created_at?: string
          updated_at?: string
        }
      }
      appointments: {
        Row: {
          id: number
          case_id: number | null
          client_id: number
          lawyer_id: number | null
          title: string
          description: string | null
          appointment_datetime: string
          duration_minutes: number
          status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show'
          meeting_link: string | null
          location: string | null
          notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          case_id?: number | null
          client_id: number
          lawyer_id?: number | null
          title: string
          description?: string | null
          appointment_datetime: string
          duration_minutes?: number
          status?: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show'
          meeting_link?: string | null
          location?: string | null
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          case_id?: number | null
          client_id?: number
          lawyer_id?: number | null
          title?: string
          description?: string | null
          appointment_datetime?: string
          duration_minutes?: number
          status?: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show'
          meeting_link?: string | null
          location?: string | null
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      payments: {
        Row: {
          id: number
          case_id: number | null
          client_id: number
          amount: number
          currency: string
          status: 'pending' | 'completed' | 'failed' | 'refunded'
          payment_method: string | null
          transaction_id: string | null
          description: string | null
          payment_data: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          case_id?: number | null
          client_id: number
          amount: number
          currency?: string
          status?: 'pending' | 'completed' | 'failed' | 'refunded'
          payment_method?: string | null
          transaction_id?: string | null
          description?: string | null
          payment_data?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          case_id?: number | null
          client_id?: number
          amount?: number
          currency?: string
          status?: 'pending' | 'completed' | 'failed' | 'refunded'
          payment_method?: string | null
          transaction_id?: string | null
          description?: string | null
          payment_data?: Json | null
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      user_role: 'client' | 'lawyer' | 'admin' | 'staff'
      case_status: 'new' | 'in_progress' | 'pending_documents' | 'under_review' | 'closed' | 'cancelled'
      case_priority: 'low' | 'medium' | 'high' | 'urgent'
      conversation_status: 'new' | 'in_progress' | 'completed' | 'escalated'
      appointment_status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show'
      payment_status: 'pending' | 'completed' | 'failed' | 'refunded'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
