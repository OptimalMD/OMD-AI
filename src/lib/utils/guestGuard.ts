import { get } from 'svelte/store';
import { user } from '$lib/stores';
import { toast } from 'svelte-sonner';
import { goto } from '$app/navigation';

/**
 * Check if current user is a guest and show warning
 * @param feature - Name of the feature being accessed
 * @returns true if user has access, false if guest
 */
export function checkGuestAccess(feature: string = 'this feature'): boolean {
	const currentUser = get(user);
	
	if (currentUser?.user_type === 'guest') {
		toast.error(`You don't have full access to ${feature}`, {
			description: 'Guest users can only access chat features. Please create an account for full access.',
			duration: 5000,
			action: {
				label: 'Create Account',
				onClick: () => goto('/auth?form=signup')
			}
		});
		return false;
	}
	
	return true;
}

/**
 * Check if current user is a guest (without showing warning)
 * @returns true if user is guest
 */
export function isGuest(): boolean {
	const currentUser = get(user);
	return currentUser?.user_type === 'guest';
}
