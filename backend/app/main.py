"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient

from app.api.router import api_router
from app.config import get_settings
from app.services.vector_service import init_collection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    try:
        from app.db.database import engine
        from app.db.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")

    # Startup: Seed demo user if not exists
    try:
        from sqlalchemy import select
        from app.db.database import async_session_factory
        from app.db.models import User
        from app.services.auth_service import hash_password
        
        async with async_session_factory() as session:
            stmt = select(User).where(User.email == "demo@coach.com")
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                demo_user = User(
                    email="demo@coach.com",
                    username="demo_user",
                    password_hash=hash_password("demopass123"),
                    display_name="Demo Candidate",
                    current_rating=1200
                )
                session.add(demo_user)
                await session.commit()
                print("Demo user seeded successfully (demo@coach.com / demopass123).")
            else:
                print("Demo user already exists.")
    except Exception as e:
        print(f"Failed to seed demo user: {e}")

    # Startup: Seed problems if not exist
    try:
        from app.db.models import Problem

        async with async_session_factory() as session:
            stmt = select(Problem).limit(1)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                seed_problems = [
                    # ── Easy (800-1000) ──────────────────────────────────────
                    Problem(
                        title="Two Sum",
                        statement=(
                            "Given an array of N integers and a target value T, find two distinct "
                            "indices i and j such that a[i] + a[j] = T. It is guaranteed that "
                            "exactly one solution exists. Return the pair of 1-indexed positions."
                        ),
                        constraints="1 ≤ N ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9, -10^9 ≤ T ≤ 10^9",
                        input_format="First line: N and T. Second line: N space-separated integers.",
                        output_format="Two space-separated 1-indexed positions i and j (i < j).",
                        sample_io=[{"input": "4 9\n2 7 11 15", "output": "1 2"}],
                        source="LeetCode",
                        source_url="https://leetcode.com/problems/two-sum/",
                        difficulty="Easy",
                        estimated_rating=800,
                        categories=["hash-table", "array"],
                        tags=["hash-map", "two-pointer", "brute-force"],
                    ),
                    Problem(
                        title="Maximum Subarray Sum",
                        statement=(
                            "Given an array of N integers (possibly negative), find the contiguous "
                            "subarray with the largest sum. Output that maximum sum. The subarray "
                            "must contain at least one element."
                        ),
                        constraints="1 ≤ N ≤ 2·10^5, -10^4 ≤ a[i] ≤ 10^4",
                        input_format="First line: N. Second line: N space-separated integers.",
                        output_format="A single integer — the maximum subarray sum.",
                        sample_io=[{"input": "9\n-2 1 -3 4 -1 2 1 -5 4", "output": "6"}],
                        source="LeetCode",
                        source_url="https://leetcode.com/problems/maximum-subarray/",
                        difficulty="Easy",
                        estimated_rating=900,
                        categories=["dp", "greedy"],
                        tags=["kadane", "prefix-sum"],
                    ),
                    Problem(
                        title="Fibonacci Number",
                        statement=(
                            "Compute the N-th Fibonacci number where F(0) = 0, F(1) = 1, and "
                            "F(n) = F(n-1) + F(n-2) for n ≥ 2. Since the answer can be very "
                            "large, output it modulo 10^9 + 7."
                        ),
                        constraints="0 ≤ N ≤ 10^6",
                        input_format="A single integer N.",
                        output_format="A single integer — F(N) mod 10^9 + 7.",
                        sample_io=[
                            {"input": "10", "output": "55"},
                            {"input": "0", "output": "0"},
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Easy",
                        estimated_rating=800,
                        categories=["dp", "math"],
                        tags=["fibonacci", "modular-arithmetic"],
                    ),
                    Problem(
                        title="Palindrome Check",
                        statement=(
                            "Given a string S consisting of lowercase English letters, determine "
                            "whether S is a palindrome. A palindrome reads the same forwards and "
                            "backwards. Output 'YES' if it is a palindrome and 'NO' otherwise."
                        ),
                        constraints="1 ≤ |S| ≤ 10^6",
                        input_format="A single line containing the string S.",
                        output_format="'YES' or 'NO'.",
                        sample_io=[
                            {"input": "racecar", "output": "YES"},
                            {"input": "hello", "output": "NO"},
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Easy",
                        estimated_rating=800,
                        categories=["strings", "two-pointer"],
                        tags=["palindrome", "string-manipulation"],
                    ),
                    Problem(
                        title="Counting Sort",
                        statement=(
                            "Given an array of N integers where each element is between 0 and K "
                            "inclusive, sort the array in non-decreasing order using counting sort. "
                            "Additionally, output the frequency of each value from 0 to K before "
                            "printing the sorted array."
                        ),
                        constraints="1 ≤ N ≤ 10^6, 0 ≤ K ≤ 10^5, 0 ≤ a[i] ≤ K",
                        input_format="First line: N and K. Second line: N space-separated integers.",
                        output_format=(
                            "First line: K+1 space-separated frequencies. "
                            "Second line: the sorted array."
                        ),
                        sample_io=[
                            {"input": "7 3\n3 1 2 3 0 1 2", "output": "1 2 2 2\n0 1 1 2 2 3 3"}
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Easy",
                        estimated_rating=1000,
                        categories=["sorting", "array"],
                        tags=["counting-sort", "frequency-array"],
                    ),
                    # ── Medium (1200-1600) ───────────────────────────────────
                    Problem(
                        title="Coin Change (Minimum Coins)",
                        statement=(
                            "You are given N coin denominations and a target amount W. Find the "
                            "minimum number of coins needed to make exactly W. Each coin denomination "
                            "can be used an unlimited number of times. If it is impossible to make "
                            "the amount, output -1."
                        ),
                        constraints="1 ≤ N ≤ 100, 1 ≤ W ≤ 10^4, 1 ≤ coin[i] ≤ W",
                        input_format="First line: N and W. Second line: N space-separated integers.",
                        output_format="A single integer — minimum coins or -1.",
                        sample_io=[
                            {"input": "3 11\n1 5 6", "output": "2"},
                            {"input": "2 3\n4 5", "output": "-1"},
                        ],
                        source="LeetCode",
                        source_url="https://leetcode.com/problems/coin-change/",
                        difficulty="Medium",
                        estimated_rating=1200,
                        categories=["dp"],
                        tags=["unbounded-knapsack", "bottom-up-dp"],
                    ),
                    Problem(
                        title="Longest Increasing Subsequence",
                        statement=(
                            "Given an array of N integers, find the length of the longest strictly "
                            "increasing subsequence. A subsequence is obtained by deleting zero or "
                            "more elements without changing the order of remaining elements."
                        ),
                        constraints="1 ≤ N ≤ 2·10^5, -10^9 ≤ a[i] ≤ 10^9",
                        input_format="First line: N. Second line: N space-separated integers.",
                        output_format="A single integer — the length of the LIS.",
                        sample_io=[
                            {"input": "8\n10 9 2 5 3 7 101 18", "output": "4"}
                        ],
                        source="LeetCode",
                        source_url="https://leetcode.com/problems/longest-increasing-subsequence/",
                        difficulty="Medium",
                        estimated_rating=1400,
                        categories=["dp", "binary-search"],
                        tags=["lis", "patience-sorting", "greedy"],
                    ),
                    Problem(
                        title="Merge Intervals",
                        statement=(
                            "Given N intervals represented as pairs [start, end], merge all overlapping "
                            "intervals and output the resulting set of non-overlapping intervals sorted "
                            "by their start value. Two intervals overlap if one starts before or when "
                            "the other ends."
                        ),
                        constraints="1 ≤ N ≤ 10^5, 0 ≤ start ≤ end ≤ 10^9",
                        input_format="First line: N. Next N lines: two integers start and end.",
                        output_format="Each line: a merged interval as two space-separated integers.",
                        sample_io=[
                            {
                                "input": "4\n1 3\n2 6\n8 10\n15 18",
                                "output": "1 6\n8 10\n15 18",
                            }
                        ],
                        source="LeetCode",
                        source_url="https://leetcode.com/problems/merge-intervals/",
                        difficulty="Medium",
                        estimated_rating=1300,
                        categories=["sorting", "greedy"],
                        tags=["intervals", "sweep-line"],
                    ),
                    Problem(
                        title="Binary Search on Answer – Aggressive Cows",
                        statement=(
                            "You have N stalls at given positions along a line and C cows. Place "
                            "the cows into stalls such that the minimum distance between any two "
                            "cows is maximized. Output that maximum possible minimum distance."
                        ),
                        constraints="2 ≤ C ≤ N ≤ 10^5, 0 ≤ position[i] ≤ 10^9",
                        input_format="First line: N and C. Second line: N space-separated positions.",
                        output_format="A single integer — the largest minimum distance.",
                        sample_io=[
                            {"input": "5 3\n1 2 4 8 9", "output": "3"}
                        ],
                        source="SPOJ",
                        source_url="https://www.spoj.com/problems/AGGRCOW/",
                        difficulty="Medium",
                        estimated_rating=1500,
                        categories=["binary-search", "greedy"],
                        tags=["binary-search-on-answer", "sorting"],
                    ),
                    Problem(
                        title="BFS Shortest Path in Unweighted Graph",
                        statement=(
                            "Given an unweighted undirected graph with N vertices and M edges, find "
                            "the shortest path (in number of edges) from vertex S to vertex T. If "
                            "no path exists, output -1. Vertices are 1-indexed."
                        ),
                        constraints="1 ≤ N ≤ 10^5, 0 ≤ M ≤ 2·10^5, 1 ≤ S, T ≤ N",
                        input_format=(
                            "First line: N, M, S, T. Next M lines: two integers u and v "
                            "denoting an edge."
                        ),
                        output_format="A single integer — the shortest distance or -1.",
                        sample_io=[
                            {"input": "5 4 1 5\n1 2\n2 3\n3 4\n4 5", "output": "4"}
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Medium",
                        estimated_rating=1600,
                        categories=["graphs", "bfs"],
                        tags=["shortest-path", "bfs", "unweighted-graph"],
                    ),
                    # ── Hard (1800-2200) ─────────────────────────────────────
                    Problem(
                        title="Segment Tree – Range Sum Query with Point Updates",
                        statement=(
                            "You are given an array of N integers. Process Q queries of two types: "
                            "(1) update the value at position i to v, and (2) compute the sum of "
                            "elements in the range [l, r]. All operations must be handled efficiently."
                        ),
                        constraints="1 ≤ N, Q ≤ 2·10^5, -10^9 ≤ a[i], v ≤ 10^9, 1 ≤ l ≤ r ≤ N",
                        input_format=(
                            "First line: N and Q. Second line: N integers. "
                            "Next Q lines: '1 i v' for update or '2 l r' for query."
                        ),
                        output_format="For each type-2 query, print the sum on a new line.",
                        sample_io=[
                            {
                                "input": "5 3\n1 2 3 4 5\n2 1 5\n1 3 10\n2 1 5",
                                "output": "15\n22",
                            }
                        ],
                        source="Codeforces",
                        source_url="https://codeforces.com/edu/course/2/lesson/4",
                        difficulty="Hard",
                        estimated_rating=1800,
                        categories=["data-structures", "segment-tree"],
                        tags=["range-query", "point-update", "segment-tree"],
                    ),
                    Problem(
                        title="Bitmask DP – Travelling Salesman Problem",
                        statement=(
                            "Given N cities and a cost matrix where cost[i][j] is the travel cost "
                            "from city i to city j, find the minimum cost to visit every city exactly "
                            "once and return to the starting city (city 0). Use bitmask dynamic "
                            "programming to solve this efficiently."
                        ),
                        constraints="2 ≤ N ≤ 20, 1 ≤ cost[i][j] ≤ 10^6",
                        input_format=(
                            "First line: N. Next N lines: N space-separated integers "
                            "representing the cost matrix."
                        ),
                        output_format="A single integer — the minimum tour cost.",
                        sample_io=[
                            {
                                "input": "4\n0 10 15 20\n10 0 35 25\n15 35 0 30\n20 25 30 0",
                                "output": "80",
                            }
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Hard",
                        estimated_rating=2000,
                        categories=["dp", "bitmask"],
                        tags=["tsp", "bitmask-dp", "hamiltonian-cycle"],
                    ),
                    Problem(
                        title="Convex Hull",
                        statement=(
                            "Given N points in the 2D plane, compute the convex hull — the smallest "
                            "convex polygon that contains all the points. Output the vertices of "
                            "the convex hull in counter-clockwise order starting from the leftmost "
                            "point (break ties by smallest y)."
                        ),
                        constraints="3 ≤ N ≤ 2·10^5, -10^9 ≤ x, y ≤ 10^9",
                        input_format="First line: N. Next N lines: two integers x and y.",
                        output_format=(
                            "First line: number of hull vertices. "
                            "Next lines: vertices in counter-clockwise order."
                        ),
                        sample_io=[
                            {
                                "input": "5\n0 0\n1 1\n2 2\n0 2\n2 0",
                                "output": "4\n0 0\n2 0\n2 2\n0 2",
                            }
                        ],
                        source="Codeforces",
                        source_url="https://codeforces.com/problemset/problem/166/B",
                        difficulty="Hard",
                        estimated_rating=2000,
                        categories=["geometry", "sorting"],
                        tags=["convex-hull", "graham-scan", "andrew-monotone-chain"],
                    ),
                    Problem(
                        title="Maximum Flow (Dinic's Algorithm)",
                        statement=(
                            "Given a directed graph with N vertices and M edges, each edge having a "
                            "capacity, find the maximum flow from source vertex S to sink vertex T. "
                            "Use an efficient max-flow algorithm such as Dinic's to handle the "
                            "constraints."
                        ),
                        constraints="2 ≤ N ≤ 500, 0 ≤ M ≤ 5000, 1 ≤ capacity ≤ 10^9",
                        input_format=(
                            "First line: N, M, S, T. Next M lines: three integers u, v, c "
                            "denoting an edge from u to v with capacity c."
                        ),
                        output_format="A single integer — the maximum flow value.",
                        sample_io=[
                            {
                                "input": "4 5 1 4\n1 2 10\n1 3 10\n2 3 2\n2 4 8\n3 4 10",
                                "output": "18",
                            }
                        ],
                        source="Codeforces",
                        source_url="https://codeforces.com/problemset/problem/546/E",
                        difficulty="Hard",
                        estimated_rating=2100,
                        categories=["graphs", "network-flow"],
                        tags=["max-flow", "dinic", "ford-fulkerson"],
                    ),
                    Problem(
                        title="Suffix Array Construction",
                        statement=(
                            "Given a string S of length N consisting of lowercase English letters, "
                            "build the suffix array — an array of indices representing all suffixes "
                            "sorted in lexicographic order. Also compute the LCP (Longest Common "
                            "Prefix) array between consecutive suffixes in the sorted order."
                        ),
                        constraints="1 ≤ N ≤ 2·10^5",
                        input_format="A single line containing the string S.",
                        output_format=(
                            "First line: N space-separated indices of the suffix array (0-indexed). "
                            "Second line: N-1 space-separated LCP values."
                        ),
                        sample_io=[
                            {
                                "input": "banana",
                                "output": "5 3 1 0 4 2\n1 3 0 0 2",
                            }
                        ],
                        source="Classic",
                        source_url=None,
                        difficulty="Hard",
                        estimated_rating=2200,
                        categories=["strings", "data-structures"],
                        tags=["suffix-array", "lcp-array", "string-sorting"],
                    ),
                ]
                session.add_all(seed_problems)
                await session.commit()
                print(f"Seeded {len(seed_problems)} competitive programming problems.")
            else:
                print("Problems already exist — skipping seed.")
    except Exception as e:
        print(f"Failed to seed problems: {e}")

    # Startup: Initialize Qdrant collection
    try:
        if settings.qdrant_api_key:
            qdrant = QdrantClient(
                url=f"https://{settings.qdrant_host}" if not settings.qdrant_host.startswith("http") else settings.qdrant_host,
                api_key=settings.qdrant_api_key,
            )
        else:
            qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        init_collection(qdrant)
    except Exception as e:
        print(f"Failed to initialize Qdrant collection: {e}")
    yield
    # Shutdown: Clean up connections if needed


app = FastAPI(
    title="Multi-Agent Competitive Programming Coach API",
    description="Backend API for Socratic CP mentoring and code review",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to the Multi-Agent Competitive Programming Coach API.",
        "docs": "/docs"
    }
