# agents/receipt_agent.py
"""
ADK-based Receipt Agent for processing receipt images and extracting data.
"""
from typing import Dict, Any, List
from agents.base_agent import StashLlmAgent
from agents.tools.receipt_tools import (
    extract_receipt_text,
    parse_receipt_data,
    store_receipt_data,
    publish_receipt_processed_event
)



class ReceiptAgent(StashLlmAgent):
    """LLM Agent specialized for receipt processing using ADK patterns."""
    
    def __init__(self):
        instruction = """You are a Receipt Processing Agent specialized in extracting and structuring data from receipt images.
        
        Your capabilities include:
        1. Extracting text from receipt images using OCR
        2. Parsing receipt text to identify merchant, items, and totals
        3. Storing processed receipt data
        4. Publishing events for downstream processing
        
        When processing a receipt:
        1. First extract text from the image using extract_receipt_text
        2. Parse the text to structure the data using parse_receipt_data
        3. Store the processed data using store_receipt_data
        4. Publish a processed event using publish_receipt_processed_event
        5. Provide a clear summary of what was extracted
        
        Always be thorough and accurate in data extraction. If you cannot extract certain information,
        clearly indicate what is missing or uncertain.
        
        For receipt processing operations, use the available tools systematically and provide detailed feedback about the results.
        """
        
        tools = [
            extract_receipt_text,
            parse_receipt_data,
            store_receipt_data,
            publish_receipt_processed_event
        ]
        
        super().__init__(
            name="ReceiptAgent",
            instruction=instruction,
            description="Processes receipt images to extract merchant, items, and financial data",
            tools=tools
        )
    
    async def process_receipt(self, image_url: str, user_id: str) -> Dict[str, Any]:
        """
        Process a receipt image through the complete pipeline.
        
        Args:
            image_url: URL or path to the receipt image
            user_id: ID of the user uploading the receipt
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Step 1: Extract text from image
            text_result = extract_receipt_text(image_url)
            
            if not text_result["success"]:
                return {
                    "status": "error",
                    "error": f"Text extraction failed: {text_result['error']}",
                    "agent": self.name
                }
            
            extracted_text = text_result["extracted_text"]
            
            # Step 2: Parse receipt data
            parse_result = parse_receipt_data(extracted_text)
            
            if not parse_result["success"]:
                return {
                    "status": "error", 
                    "error": f"Receipt parsing failed: {parse_result['error']}",
                    "agent": self.name
                }
            
            receipt_data = {
                "merchant": parse_result["merchant"],
                "items": parse_result["items"],
                "total": parse_result["total"]
            }
            
            # Step 3: Store receipt data
            store_result = store_receipt_data(user_id, receipt_data, image_url)
            
            if not store_result["success"]:
                return {
                    "status": "error",
                    "error": f"Storage failed: {store_result['error']}",
                    "agent": self.name
                }
            
            # Step 4: Publish processed event
            publish_result = publish_receipt_processed_event(store_result["data"])
            
            # Return comprehensive result
            return {
                "status": "success",
                "receipt_id": store_result["receipt_id"],
                "data": store_result["data"],
                "processing_summary": {
                    "text_extracted": len(extracted_text) > 0,
                    "merchant_found": receipt_data["merchant"] != "Unknown",
                    "items_parsed": len(receipt_data["items"]),
                    "total_amount": receipt_data["total"],
                    "stored_successfully": True,
                    "event_published": publish_result["success"]
                },
                "agent": self.name
            }
            
        except Exception as e:
            error_msg = f"Receipt processing failed: {str(e)}"
            return {
                "status": "error",
                "error": error_msg,
                "agent": self.name
            }
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requests for receipt-related operations.
        
        Args:
            request: Request containing operation type and parameters
            
        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "process_receipt")
        
        if operation == "process_receipt":
            image_url = request.get("imageUrl")
            user_id = request.get("userId")
            
            if not image_url or not user_id:
                return {
                    "status": "error",
                    "error": "imageUrl and userId are required for receipt processing",
                    "agent": self.name
                }
            
            return await self.process_receipt(image_url, user_id)
        
        else:
            # Use the base ADK processing for other queries
            return await self.process_stash_request(request)
