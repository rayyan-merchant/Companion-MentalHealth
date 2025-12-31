from backend.main import run_reasoning_pipeline, KrrRequest
import asyncio
import os

# Ensure directories exist for session persistence
os.makedirs("data/session_graphs", exist_ok=True)

async def test_krr_run():
    print("Testing /api/krr/run Logic (Direct Call)...")
    
    # Construct Request Model
    request = KrrRequest(
        session_id="test-session-int-002",
        student_id="student_test_user_2",
        text="I feel overwhelmed by my coursework deadlines."
    )
    
    try:
        # Call Endpoint Handler directly
        response = await run_reasoning_pipeline(request)
        
        print("Response received.")
        print(f"Session ID: {response.session_id}")
        print(f"Summary: {response.summary}")
        print(f"Explanations: {response.explanations}")
        print(f"Ranked Concern: {response.ranked_concerns}")
        
        # Verify Contract
        assert response.session_id == request.session_id
        assert response.audit_ref is not None
        print("✅ Contract Verified (Direct Logic)")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_krr_run())

