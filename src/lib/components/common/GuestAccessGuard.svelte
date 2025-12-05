<script lang="ts">
	import { user } from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	export let feature: string = 'this feature';

	const showUpgradeMessage = () => {
		toast.error(`You don't have full access to ${feature}`, {
			description: 'Guest users can only access chat features. Please create an account for full access.',
			duration: 5000,
			action: {
				label: 'Create Account',
				onClick: () => goto('/auth?form=signup')
			}
		});
	};

	export const checkAccess = (): boolean => {
		if ($user?.user_type === 'guest') {
			showUpgradeMessage();
			return false;
		}
		return true;
	};
</script>
