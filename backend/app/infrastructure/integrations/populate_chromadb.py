#!/usr/bin/env python3
"""
ChromaDB Population Script for Dubai Real Estate RAG System
This script populates all ChromaDB collections with sample data for intelligent assistant functionality
"""

import os
import sys
import json
import chromadb
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChromaDBPopulator:
    def __init__(self, chroma_host: str, chroma_port: int):
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

        # Sample data for each collection
        self.sample_data = {
            "market_analysis": [
                {
                    "content": "Dubai real estate market shows strong recovery in 2024 with 15% price increase in luxury segment. Transaction volumes up 25% compared to 2023. Dubai Marina and Downtown remain top investment destinations with average rental yields of 6.5%.",
                    "metadata": {
                        "type": "market_trend",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "RERA",
                    },
                },
                {
                    "content": "Off-plan properties in Dubai South and Dubai Creek Harbour experiencing 20% price appreciation. Foreign investment from UK, India, and China driving market growth. Golden Visa program contributing to increased demand.",
                    "metadata": {
                        "type": "investment_analysis",
                        "area": "Dubai South",
                        "period": "2024",
                        "source": "DLD",
                    },
                },
                {
                    "content": "Dubai property market forecast: 8-12% growth expected in 2025. Palm Jumeirah villas showing highest appreciation at 18%. Apartment segment stable with 5-7% growth projected.",
                    "metadata": {
                        "type": "forecast",
                        "area": "Dubai",
                        "period": "2025",
                        "source": "Market Analysis",
                    },
                },
            ],
            "regulatory_framework": [
                {
                    "content": "Golden Visa requirements: Property investment of AED 2M+ qualifies for 10-year residency. Off-plan properties require 50% down payment. RERA escrow account mandatory for all off-plan sales.",
                    "metadata": {
                        "type": "visa_regulations",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "GDRFA",
                    },
                },
                {
                    "content": "RERA Law No. 3 of 2002: All real estate agents must be licensed. Commission capped at 2% for residential, 4% for commercial. Mandatory disclosure of all fees and charges to clients.",
                    "metadata": {
                        "type": "agent_regulations",
                        "area": "Dubai",
                        "period": "2002",
                        "source": "RERA",
                    },
                },
                {
                    "content": "Dubai Land Department regulations: All property transactions must be registered. Transfer fees: 4% for first-time buyers, 8% for investors. NOC required from developer for resale of off-plan properties.",
                    "metadata": {
                        "type": "transaction_regulations",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "DLD",
                    },
                },
            ],
            "neighborhood_profiles": [
                {
                    "content": "Dubai Marina: Luxury waterfront community with 200+ restaurants, 5-star hotels, and world-class amenities. Average apartment price: AED 2.5M. Rental yield: 6.8%. Popular with expats and investors.",
                    "metadata": {
                        "type": "neighborhood_profile",
                        "area": "Dubai Marina",
                        "period": "2024",
                        "source": "Area Guide",
                    },
                },
                {
                    "content": "Downtown Dubai: Home to Burj Khalifa and Dubai Mall. Ultra-luxury properties with average price of AED 4M+. Rental yield: 5.2%. High demand from international investors and luxury buyers.",
                    "metadata": {
                        "type": "neighborhood_profile",
                        "area": "Downtown Dubai",
                        "period": "2024",
                        "source": "Area Guide",
                    },
                },
                {
                    "content": "Palm Jumeirah: Exclusive island community with private beaches. Villa prices range from AED 8M to 50M+. Rental yield: 4.5%. Limited supply driving high appreciation rates.",
                    "metadata": {
                        "type": "neighborhood_profile",
                        "area": "Palm Jumeirah",
                        "period": "2024",
                        "source": "Area Guide",
                    },
                },
            ],
            "investment_insights": [
                {
                    "content": "Dubai real estate investment strategy: Focus on off-plan properties in emerging areas like Dubai South and Dubai Creek Harbour. Expected ROI: 15-25% over 3-5 years. Consider Golden Visa benefits for long-term investment.",
                    "metadata": {
                        "type": "investment_strategy",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Investment Guide",
                    },
                },
                {
                    "content": "Rental investment analysis: Dubai Marina apartments offer best rental yields at 6.8%. Downtown Dubai luxury apartments: 5.2% yield. Palm Jumeirah villas: 4.5% yield but higher capital appreciation.",
                    "metadata": {
                        "type": "rental_analysis",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Rental Market Report",
                    },
                },
                {
                    "content": "Foreign investment opportunities: UK investors benefit from strong GBP-AED exchange rate. Indian investors can use NRE accounts. Chinese investors prefer luxury segment in Downtown and Palm Jumeirah.",
                    "metadata": {
                        "type": "foreign_investment",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "International Investment Guide",
                    },
                },
            ],
            "developer_profiles": [
                {
                    "content": "Emaar Properties: Dubai's largest developer with 40% market share. Key projects: Burj Khalifa, Dubai Mall, Downtown Dubai. Reputation score: 9.2/10. Strong track record of on-time delivery.",
                    "metadata": {
                        "type": "developer_profile",
                        "developer": "Emaar",
                        "period": "2024",
                        "source": "Developer Database",
                    },
                },
                {
                    "content": "DAMAC Properties: Luxury developer specializing in high-end properties. Key projects: DAMAC Hills, AKOYA Oxygen. Reputation score: 8.5/10. Known for innovative designs and premium amenities.",
                    "metadata": {
                        "type": "developer_profile",
                        "developer": "DAMAC",
                        "period": "2024",
                        "source": "Developer Database",
                    },
                },
                {
                    "content": "Nakheel: Government-owned developer behind Palm Jumeirah and Dubai Islands. Reputation score: 8.8/10. Strong financial backing and large-scale project expertise.",
                    "metadata": {
                        "type": "developer_profile",
                        "developer": "Nakheel",
                        "period": "2024",
                        "source": "Developer Database",
                    },
                },
            ],
            "transaction_guidance": [
                {
                    "content": "Property buying process in Dubai: 1) Choose property and developer 2) Sign MOU and pay booking fee 3) Apply for mortgage if needed 4) Sign SPA and pay down payment 5) Register with DLD 6) Complete payment and get title deed.",
                    "metadata": {
                        "type": "buying_process",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Transaction Guide",
                    },
                },
                {
                    "content": "Mortgage requirements: Minimum 25% down payment for expats, 20% for UAE nationals. Maximum loan term: 25 years. Interest rates: 3.5-5.5% depending on bank and profile.",
                    "metadata": {
                        "type": "mortgage_guide",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Banking Guide",
                    },
                },
                {
                    "content": "Property selling process: 1) Get NOC from developer if off-plan 2) List with licensed agent 3) Negotiate with buyer 4) Sign SPA 5) Complete transfer at DLD 6) Pay transfer fees and receive payment.",
                    "metadata": {
                        "type": "selling_process",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Transaction Guide",
                    },
                },
            ],
            "market_forecasts": [
                {
                    "content": "Dubai real estate forecast 2025: Overall market growth of 8-12%. Luxury segment: 15-20% growth. Mid-market: 5-8% growth. Off-plan properties: 20-25% growth in emerging areas.",
                    "metadata": {
                        "type": "market_forecast",
                        "area": "Dubai",
                        "period": "2025",
                        "source": "Market Research",
                    },
                },
                {
                    "content": "Dubai 2040 Urban Master Plan: Population to reach 5.8M by 2040. New areas: Dubai South, Dubai Creek Harbour, Dubai Islands. Focus on sustainable development and smart city initiatives.",
                    "metadata": {
                        "type": "urban_planning",
                        "area": "Dubai",
                        "period": "2040",
                        "source": "Dubai 2040 Plan",
                    },
                },
                {
                    "content": "Technology impact on real estate: Virtual tours becoming standard. AI-powered property matching. Blockchain for property transactions. Smart home integration increasing property values.",
                    "metadata": {
                        "type": "tech_forecast",
                        "area": "Dubai",
                        "period": "2025",
                        "source": "Tech Analysis",
                    },
                },
            ],
            "agent_resources": [
                {
                    "content": "Sales techniques for Dubai real estate: 1) Understand client's investment goals 2) Highlight Golden Visa benefits 3) Show market data and growth potential 4) Emphasize developer track record 5) Provide financing options 6) Follow up consistently.",
                    "metadata": {
                        "type": "sales_techniques",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Agent Training",
                    },
                },
                {
                    "content": "Client objection handling: Price concerns - show market appreciation data. Location doubts - provide area guides and amenities. Developer worries - share track record and reviews. Financing issues - connect with mortgage specialists.",
                    "metadata": {
                        "type": "objection_handling",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Agent Training",
                    },
                },
                {
                    "content": "Closing strategies: Create urgency with limited availability. Offer financing solutions. Provide comprehensive market analysis. Build trust through transparency. Follow up with personalized service.",
                    "metadata": {
                        "type": "closing_strategies",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Agent Training",
                    },
                },
            ],
            "urban_planning": [
                {
                    "content": "Dubai 2040 Urban Master Plan: Transform Dubai into world's best city to live and work. 5 strategic goals: 1) Enhance quality of life 2) Increase economic competitiveness 3) Strengthen global position 4) Ensure environmental sustainability 5) Foster social cohesion.",
                    "metadata": {
                        "type": "master_plan",
                        "area": "Dubai",
                        "period": "2040",
                        "source": "Dubai 2040 Plan",
                    },
                },
                {
                    "content": "Dubai South: Future aviation hub and smart city. 145 sq km development. Home to Expo 2020 site and Al Maktoum International Airport. Expected population: 1M by 2040. Major investment opportunities.",
                    "metadata": {
                        "type": "development_zone",
                        "area": "Dubai South",
                        "period": "2040",
                        "source": "Urban Planning",
                    },
                },
                {
                    "content": "Dubai Creek Harbour: New downtown development. 6 sq km waterfront city. Home to Dubai Creek Tower (tallest building in world). Mixed-use development with residential, commercial, and tourism components.",
                    "metadata": {
                        "type": "development_zone",
                        "area": "Dubai Creek Harbour",
                        "period": "2040",
                        "source": "Urban Planning",
                    },
                },
            ],
            "financial_insights": [
                {
                    "content": "Dubai mortgage market: Interest rates range from 3.5% to 5.5%. Maximum loan amount: 80% of property value for UAE nationals, 75% for expats. Popular banks: Emirates NBD, Dubai Islamic Bank, Abu Dhabi Commercial Bank.",
                    "metadata": {
                        "type": "mortgage_market",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Banking Analysis",
                    },
                },
                {
                    "content": "Investment financing options: Conventional mortgages, Islamic financing, developer payment plans, cash purchases. Islamic financing growing in popularity with 30% market share. Developer plans offer 0% interest for 1-3 years.",
                    "metadata": {
                        "type": "financing_options",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Financial Guide",
                    },
                },
                {
                    "content": "Tax benefits for Dubai real estate: No property tax, no capital gains tax, no income tax on rental income. Only costs: service charges, maintenance fees, and transfer fees. Makes Dubai attractive for international investors.",
                    "metadata": {
                        "type": "tax_benefits",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Tax Analysis",
                    },
                },
            ],
            "real_estate_docs": [
                {
                    "content": "Dubai real estate market overview: Dynamic market with strong fundamentals. Population growth, economic diversification, and government initiatives driving demand. Foreign investment friendly with Golden Visa program.",
                    "metadata": {
                        "type": "market_overview",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Market Report",
                    },
                },
                {
                    "content": "Property types in Dubai: Apartments (studios to penthouses), Villas (3-7 bedrooms), Townhouses, Penthouses, Duplexes. Each type offers different investment potential and rental yields.",
                    "metadata": {
                        "type": "property_types",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Property Guide",
                    },
                },
                {
                    "content": "Dubai real estate terminology: Freehold (foreign ownership allowed), Leasehold (99-year lease), Off-plan (under construction), Ready (completed), SPA (Sales and Purchase Agreement), NOC (No Objection Certificate).",
                    "metadata": {
                        "type": "terminology",
                        "area": "Dubai",
                        "period": "2024",
                        "source": "Legal Guide",
                    },
                },
            ],
        }

    def create_collections(self):
        """Create all ChromaDB collections"""
        collections_created = []

        for collection_name in self.sample_data.keys():
            try:
                # Get or create collection
                collection = self.chroma_client.get_or_create_collection(
                    collection_name
                )
                collections_created.append(collection_name)
                logger.info(f"✅ Created/accessed collection: {collection_name}")
            except Exception as e:
                logger.error(f"❌ Error creating collection {collection_name}: {e}")

        return collections_created

    def populate_collections(self):
        """Populate all collections with sample data"""
        total_documents = 0

        for collection_name, documents in self.sample_data.items():
            try:
                collection = self.chroma_client.get_collection(collection_name)

                # Prepare data for insertion
                docs = []
                metadatas = []
                ids = []

                for i, doc in enumerate(documents):
                    docs.append(doc["content"])
                    metadatas.append(doc["metadata"])
                    ids.append(f"{collection_name}_{i}")

                # Add documents to collection
                if docs:
                    collection.add(documents=docs, metadatas=metadatas, ids=ids)
                    total_documents += len(docs)
                    logger.info(f"✅ Added {len(docs)} documents to {collection_name}")

            except Exception as e:
                logger.error(f"❌ Error populating collection {collection_name}: {e}")

        return total_documents

    def verify_collections(self):
        """Verify that collections are populated"""
        verification_results = {}

        for collection_name in self.sample_data.keys():
            try:
                collection = self.chroma_client.get_collection(collection_name)
                count = collection.count()
                verification_results[collection_name] = count
                logger.info(f"📊 Collection {collection_name}: {count} documents")
            except Exception as e:
                logger.error(f"❌ Error verifying collection {collection_name}: {e}")
                verification_results[collection_name] = 0

        return verification_results

    def run_population(self):
        """Run complete ChromaDB population process"""
        try:
            logger.info("🚀 Starting ChromaDB population...")

            # Create collections
            collections = self.create_collections()
            logger.info(f"✅ Created {len(collections)} collections")

            # Populate collections
            total_docs = self.populate_collections()
            logger.info(f"✅ Added {total_docs} total documents")

            # Verify collections
            verification = self.verify_collections()

            logger.info("🎉 ChromaDB population completed successfully!")
            return {
                "collections_created": len(collections),
                "total_documents": total_docs,
                "verification": verification,
            }

        except Exception as e:
            logger.error(f"❌ Error during ChromaDB population: {e}")
            raise


def main():
    """Main function to run ChromaDB population"""
    try:
        # Get ChromaDB connection details from environment variables
        chroma_host = os.getenv("CHROMA_HOST")
        chroma_port = os.getenv("CHROMA_PORT")

        if not chroma_host or not chroma_port:
            logger.error("❌ CHROMA_HOST or CHROMA_PORT environment variables not set.")
            sys.exit(1)

        # Pass the correct host and port to the populator
        populator = ChromaDBPopulator(
            chroma_host=chroma_host, chroma_port=int(chroma_port)
        )
        results = populator.run_population()

        print("\n" + "=" * 60)
        print("🎉 CHROMADB POPULATION COMPLETED!")
        print("=" * 60)
        print(f"✅ Collections created: {results['collections_created']}")
        print(f"✅ Total documents added: {results['total_documents']}")
        print("\n📊 Collection Verification:")
        for collection, count in results["verification"].items():
            print(f"   - {collection}: {count} documents")
        print("\nYour RAG system now has comprehensive Dubai real estate data!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to populate ChromaDB: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
