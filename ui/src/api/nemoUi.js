export async function fetchLandingData() {
  const response = await fetch('/api/ui/landing/', {
    headers: { 'Accept': 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`Failed to load landing data: ${response.status}`);
  }

  return response.json();
}
