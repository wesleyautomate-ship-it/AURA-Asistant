export interface SeededListing {
  listingId: string;
  title: string;
  location: string;
  priceAED: number;
}

export const seededListings: SeededListing[] = [
  {
    listingId: 'LST-000001',
    title: '3BR Townhouse in Burj Vista',
    location: 'Downtown Dubai',
    priceAED: 2961890
  },
  {
    listingId: 'LST-000002',
    title: '1BR Studio in Bay Views',
    location: 'Business Bay',
    priceAED: 1500000
  },
  {
    listingId: 'LST-000003',
    title: '1BR Studio in Jumeirah Central',
    location: 'Jumeirah',
    priceAED: 1500000
  },
  {
    listingId: 'LST-000004',
    title: '4BR Apartment in The Address',
    location: 'Downtown Dubai',
    priceAED: 2632182
  }
];

export const pickRandomSeededListing = (): SeededListing => {
  if (seededListings.length === 0) {
    throw new Error('No seeded listings available');
  }
  const index = Math.floor(Math.random() * seededListings.length);
  return seededListings[index];
};
