import api from '@/utils/axios'
import type { User } from '@/types'

/**
 * Search for users by email
 * @param email Email to search for
 * @returns Array of matching users
 */
export async function searchUsersByEmail(email: string): Promise<User[]> {
  try {
    console.log(`Searching for users with email: ${email}`);
    
    const { data } = await api.get(`/api/users/search?email=${encodeURIComponent(email)}`);
    
    console.log('Search response data:', data);
    
    if (Array.isArray(data)) {
      console.log('Found users:', data.length);
      
      // Verify each user has the required fields
      const mappedUsers = data.map(user => {
        console.log('Processing user:', user);
        
        // Ensure each user has the right fields
        return {
          ...user,
          uuid: user.uuid,
          email: user.email || '',
          name: user.name || 'Unknown User'
        };
      });
      
      console.log('Mapped users:', mappedUsers);
      return mappedUsers;
    }
    
    console.warn('Unexpected data format:', data);
    return [];
  } catch (error) {
    console.error('Error searching users by email:', error);
    return [];
  }
}

/**
 * Get user by ID
 * @param userId User UUID
 * @returns User object
 */
export async function getUserById(userId: string): Promise<User> {
  const { data } = await api.get(`/api/users/${userId}`)
  return data
} 