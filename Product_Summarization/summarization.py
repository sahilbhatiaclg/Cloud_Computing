"""
Azure AI Language Services - Comprehensive Text Analysis
Features:
- Automatic Language Detection
- Named Entity Recognition (Brands, Prices, Locations, etc.)
- Text Summarization
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import requests
import json

class TextAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Text Analysis - Language Services")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")
        
        # Azure Language Service credentials
        self.api_key = ""
        self.endpoint = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg="#0078D4", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🧠 Azure AI Language Services - Text Analysis", 
                font=("Segoe UI", 20, "bold"), bg="#0078D4", fg="white").pack(pady=18)
        
        # ==================== MAIN CONTAINER ====================
        container = tk.Frame(self.root, bg="#f5f5f5")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # ==================== CREDENTIALS ====================
        cred_frame = tk.LabelFrame(container, text=" Azure Language Service Credentials ", 
                                  font=("Segoe UI", 10, "bold"), bg="white", 
                                  fg="#0078D4", relief=tk.GROOVE, bd=2)
        cred_frame.pack(fill=tk.X, pady=(0, 15))
        
        cred_content = tk.Frame(cred_frame, bg="white")
        cred_content.pack(padx=15, pady=12)
        
        tk.Label(cred_content, text="API Key:", bg="white", 
                font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.key_entry = tk.Entry(cred_content, show="*", font=("Segoe UI", 9), 
                                 width=50, bg="#f9f9f9", relief=tk.SOLID, bd=1)
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(cred_content, text="Endpoint:", bg="white", 
                font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.endpoint_entry = tk.Entry(cred_content, font=("Segoe UI", 9), 
                                      width=50, bg="#f9f9f9", relief=tk.SOLID, bd=1)
        self.endpoint_entry.insert(0, "https://YOUR-RESOURCE.cognitiveservices.azure.com/")
        self.endpoint_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # ==================== INPUT SECTION ====================
        input_frame = tk.LabelFrame(container, text=" 📝 Input Text (Product Description / Long Text) ", 
                                   font=("Segoe UI", 10, "bold"), bg="white", 
                                   fg="#0078D4", relief=tk.GROOVE, bd=2)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        input_content = tk.Frame(input_frame, bg="white")
        input_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        self.input_text = scrolledtext.ScrolledText(input_content, wrap=tk.WORD, 
                                                    font=("Segoe UI", 10), height=8,
                                                    bg="#f9f9f9", relief=tk.SOLID, bd=1,
                                                    padx=10, pady=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.insert(1.0, 
            "Apple iPhone 15 Pro Max is now available in New York for $1,199. "
            "This flagship smartphone features a titanium design, A17 Pro chip, "
            "and an advanced camera system with 5x optical zoom. The device is "
            "manufactured by Apple Inc. and is available at Best Buy stores across "
            "the United States. The phone comes with 256GB storage and includes "
            "features like Dynamic Island, always-on display, and supports 5G connectivity. "
            "Customers in Los Angeles and Chicago can get special discounts of $100 off.")
        
        # ==================== BUTTONS ====================
        button_frame = tk.Frame(container, bg="#f5f5f5")
        button_frame.pack(pady=10)
        
        self.analyze_btn = tk.Button(button_frame, text="🔍 Analyze Text", 
                                     command=self.analyze_text,
                                     bg="#0078D4", fg="white", font=("Segoe UI", 11, "bold"),
                                     padx=30, pady=12, cursor="hand2", relief=tk.FLAT)
        self.analyze_btn.pack(side=tk.LEFT, padx=8)
        
        self.clear_btn = tk.Button(button_frame, text="🗑 Clear All", 
                                   command=self.clear_all,
                                   bg="#D13438", fg="white", font=("Segoe UI", 11, "bold"),
                                   padx=30, pady=12, cursor="hand2", relief=tk.FLAT)
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        
        # ==================== RESULTS SECTION ====================
        results_container = tk.Frame(container, bg="#f5f5f5")
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Language & Entities
        left_col = tk.Frame(results_container, bg="#f5f5f5")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Language Detection
        lang_frame = tk.LabelFrame(left_col, text=" 🌐 Detected Language ", 
                                  font=("Segoe UI", 10, "bold"), bg="white", 
                                  fg="#107C10", relief=tk.GROOVE, bd=2)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lang_result = tk.Text(lang_frame, wrap=tk.WORD, font=("Segoe UI", 10), 
                                  height=3, bg="#f0f8f0", relief=tk.FLAT,
                                  padx=10, pady=10)
        self.lang_result.pack(fill=tk.X, padx=10, pady=10)
        self.lang_result.config(state=tk.DISABLED)
        
        # Entity Recognition
        entity_frame = tk.LabelFrame(left_col, text=" 🏷 Extracted Entities (Brands, Prices, Locations) ", 
                                    font=("Segoe UI", 10, "bold"), bg="white", 
                                    fg="#8661C5", relief=tk.GROOVE, bd=2)
        entity_frame.pack(fill=tk.BOTH, expand=True)
        
        self.entity_result = scrolledtext.ScrolledText(entity_frame, wrap=tk.WORD, 
                                                      font=("Segoe UI", 9), height=12,
                                                      bg="#f9f4ff", relief=tk.FLAT,
                                                      padx=10, pady=10)
        self.entity_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entity_result.config(state=tk.DISABLED)
        
        # Right column - Summary
        right_col = tk.Frame(results_container, bg="#f5f5f5")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        summary_frame = tk.LabelFrame(right_col, text=" 📋 Generated Summary ", 
                                     font=("Segoe UI", 10, "bold"), bg="white", 
                                     fg="#FF8C00", relief=tk.GROOVE, bd=2)
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        self.summary_result = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                       font=("Segoe UI", 10), height=18,
                                                       bg="#fff8f0", relief=tk.FLAT,
                                                       padx=10, pady=10)
        self.summary_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.summary_result.config(state=tk.DISABLED)
        
        # ==================== STATUS BAR ====================
        self.status_bar = tk.Label(self.root, text="Ready | Enter text and click Analyze", 
                                  bg="#333333", fg="white", font=("Segoe UI", 9),
                                  anchor=tk.W, padx=15, pady=8)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def analyze_text(self):
        """Perform comprehensive text analysis"""
        # Get credentials
        self.api_key = self.key_entry.get().strip()
        self.endpoint = self.endpoint_entry.get().strip().rstrip('/')
        
        if not self.api_key or not self.endpoint:
            messagebox.showwarning("Missing Credentials", 
                                 "Please enter your Azure Language Service API Key and Endpoint")
            return
        
        # Get text
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("No Text", "Please enter text to analyze")
            return
        
        self.status_bar.config(text="⏳ Analyzing text...")
        self.analyze_btn.config(state=tk.DISABLED, text="Analyzing...")
        self.root.update()
        
        try:
            # Perform all analyses
            self.detect_language(text)
            self.extract_entities(text)
            self.summarize_text(text)
            
            self.status_bar.config(text="✅ Analysis completed successfully!")
        
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze text:\n{str(e)}")
            self.status_bar.config(text="❌ Analysis failed")
        
        finally:
            self.analyze_btn.config(state=tk.NORMAL, text="🔍 Analyze Text")
    
    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            url = f"{self.endpoint}/text/analytics/v3.1/languages"
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "documents": [
                    {
                        "id": "1",
                        "text": text
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                lang = result['documents'][0]['detectedLanguage']
                
                output = f"Language: {lang['name']}\n"
                output += f"Code: {lang['iso6391Name']}\n"
                output += f"Confidence: {lang['confidenceScore']:.2%}"
                
                self.lang_result.config(state=tk.NORMAL)
                self.lang_result.delete(1.0, tk.END)
                self.lang_result.insert(1.0, output)
                self.lang_result.config(state=tk.DISABLED)
            else:
                raise Exception(f"Language detection failed: {response.status_code}")
        
        except Exception as e:
            self.lang_result.config(state=tk.NORMAL)
            self.lang_result.delete(1.0, tk.END)
            self.lang_result.insert(1.0, f"Error: {str(e)}")
            self.lang_result.config(state=tk.DISABLED)
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        try:
            url = f"{self.endpoint}/text/analytics/v3.1/entities/recognition/general"
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "documents": [
                    {
                        "id": "1",
                        "language": "en",
                        "text": text
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                entities = result['documents'][0]['entities']
                
                # Group entities by category
                grouped = {}
                for entity in entities:
                    category = entity['category']
                    if category not in grouped:
                        grouped[category] = []
                    grouped[category].append({
                        'text': entity['text'],
                        'confidence': entity['confidenceScore']
                    })
                
                # Format output
                output = ""
                
                # Priority categories
                priority = ['Product', 'Organization', 'Location', 'Person', 'Quantity', 'DateTime']
                
                for category in priority:
                    if category in grouped:
                        output += f"\n{'='*50}\n"
                        output += f"📌 {category.upper()}\n"
                        output += f"{'='*50}\n"
                        for item in grouped[category]:
                            output += f"  • {item['text']} (Confidence: {item['confidence']:.2%})\n"
                        del grouped[category]
                
                # Other categories
                for category, items in grouped.items():
                    output += f"\n{'='*50}\n"
                    output += f"📌 {category.upper()}\n"
                    output += f"{'='*50}\n"
                    for item in items:
                        output += f"  • {item['text']} (Confidence: {item['confidence']:.2%})\n"
                
                if not output:
                    output = "No entities detected."
                
                self.entity_result.config(state=tk.NORMAL)
                self.entity_result.delete(1.0, tk.END)
                self.entity_result.insert(1.0, output.strip())
                self.entity_result.config(state=tk.DISABLED)
            else:
                raise Exception(f"Entity extraction failed: {response.status_code}")
        
        except Exception as e:
            self.entity_result.config(state=tk.NORMAL)
            self.entity_result.delete(1.0, tk.END)
            self.entity_result.insert(1.0, f"Error: {str(e)}")
            self.entity_result.config(state=tk.DISABLED)
    
    def summarize_text(self, text):
        """Generate extractive summary of text"""
        try:
            # Split text into sentences
            import re
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if len(sentences) < 3:
                self.summary_result.config(state=tk.NORMAL)
                self.summary_result.delete(1.0, tk.END)
                self.summary_result.insert(1.0, "Text is too short for summarization. Need at least 3 sentences.")
                self.summary_result.config(state=tk.DISABLED)
                return
            
            # Try Azure's extractive summarization API
            url = f"{self.endpoint}/language/analyze-text/jobs?api-version=2023-04-01"
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "displayName": "Text Summarization",
                "analysisInput": {
                    "documents": [
                        {
                            "id": "1",
                            "language": "en",
                            "text": text
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "ExtractiveSummarization",
                        "parameters": {
                            "sentenceCount": min(3, len(sentences))
                        }
                    }
                ]
            }
            
            # Submit job
            response = requests.post(url, headers=headers, json=body, timeout=10)
            
            if response.status_code == 202:
                # Get the operation location
                operation_location = response.headers.get('Operation-Location')
                
                if operation_location:
                    # Poll for results
                    import time
                    max_attempts = 15
                    attempt = 0
                    
                    while attempt < max_attempts:
                        time.sleep(2)
                        result_response = requests.get(operation_location, headers=headers, timeout=10)
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            
                            if result_data['status'] == 'succeeded':
                                tasks = result_data['tasks']['items']
                                
                                summary_sentences = []
                                for task in tasks:
                                    if task['kind'] == 'ExtractiveSummarizationLMResults':
                                        if 'results' in task and 'documents' in task['results']:
                                            if len(task['results']['documents']) > 0:
                                                doc_result = task['results']['documents'][0]
                                                if 'sentences' in doc_result:
                                                    results = doc_result['sentences']
                                                    summary_sentences = [s['text'] for s in results]
                                        break
                                
                                if summary_sentences:
                                    output = "📋 EXTRACTIVE SUMMARY:\n\n"
                                    output += " ".join(summary_sentences)
                                    output += f"\n\n✅ Successfully extracted {len(summary_sentences)} key sentence(s) from the text."
                                else:
                                    # Fallback to simple extraction
                                    summary_sentences = sentences[:3]
                                    output = "📋 KEY SENTENCES (Manual Extraction):\n\n"
                                    output += ". ".join(summary_sentences) + "."
                                    output += "\n\n⚠️ Note: Azure extractive summarization returned no results. Using first 3 sentences."
                                
                                self.summary_result.config(state=tk.NORMAL)
                                self.summary_result.delete(1.0, tk.END)
                                self.summary_result.insert(1.0, output)
                                self.summary_result.config(state=tk.DISABLED)
                                return
                            
                            elif result_data['status'] == 'failed':
                                error_msg = result_data.get('errors', [{}])[0].get('message', 'Unknown error')
                                raise Exception(f"Summarization failed: {error_msg}")
                        
                        attempt += 1
                    
                    raise Exception("Summarization polling timed out after 30 seconds")
                else:
                    raise Exception("No operation location received from Azure")
            else:
                error_text = response.text
                raise Exception(f"API request failed with status {response.status_code}: {error_text}")
        
        except Exception as e:
            # Fallback: Use simple sentence extraction
            self.summary_result.config(state=tk.NORMAL)
            self.summary_result.delete(1.0, tk.END)
            
            # Extract first 3 meaningful sentences
            import re
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if len(sentences) >= 3:
                summary_sentences = sentences[:3]
                output = "📋 KEY SENTENCES (Fallback Method):\n\n"
                output += ". ".join(summary_sentences) + "."
                output += f"\n\n⚠️ Azure Summarization Error: {str(e)}"
                output += "\n\nUsing simple extraction of first 3 sentences as fallback."
            else:
                output = f"❌ Cannot summarize: Text has only {len(sentences)} sentence(s). Need at least 3 sentences."
                output += f"\n\nError: {str(e)}"
            
            self.summary_result.insert(1.0, output)
            self.summary_result.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear all fields"""
        self.input_text.delete(1.0, tk.END)
        
        self.lang_result.config(state=tk.NORMAL)
        self.lang_result.delete(1.0, tk.END)
        self.lang_result.config(state=tk.DISABLED)
        
        self.entity_result.config(state=tk.NORMAL)
        self.entity_result.delete(1.0, tk.END)
        self.entity_result.config(state=tk.DISABLED)
        
        self.summary_result.config(state=tk.NORMAL)
        self.summary_result.delete(1.0, tk.END)
        self.summary_result.config(state=tk.DISABLED)
        
        self.status_bar.config(text="Cleared | Ready for new analysis")


def main():
    root = tk.Tk()
    app = TextAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()