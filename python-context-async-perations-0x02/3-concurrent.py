import asyncio
import aiosqlite

async def async_fetch_users():
    # Ouvre une connexion asynchrone
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("Tous les utilisateurs:")
            for row in results:
                print(row)
            return results

async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print("\nUtilisateurs de plus de 40 ans:")
            for row in results:
                print(row)
            return results

async def fetch_concurrently():
    # Exécute les deux requêtes en même temps
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Lance le tout
asyncio.run(fetch_concurrently())