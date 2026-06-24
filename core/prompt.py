"""
Prompt模板管理器
统一管理所有Prompt模板，避免重复定义
"""

class PromptBuilder:
    """Prompt构建器，支持多种模板和上下文限制"""
    
    def __init__(self, max_context_length: int = 3000):
        """
        初始化Prompt构建器
        
        Args:
            max_context_length: 最大上下文长度，默认为3000字符
        """
        self.max_context_length = max_context_length
        
    def build_rag_prompt(self, query: str, docs: list) -> dict:
        """
        构建RAG问答Prompt
        
        Args:
            query: 用户问题
            docs: 检索到的文档列表（包含metadata）
            
        Returns:
            dict: {prompt, sources, context_length}
        """
        # 收集来源信息
        sources = []
        seen = set()
        
        # 构建上下文（带精确引用）
        context_parts = []
        total_length = 0
        
        for idx, doc in enumerate(docs):
            # 提取metadata
            source = doc.metadata.get("source", "未知来源")
            chunk_id = doc.metadata.get("chunk_id", idx + 1)
            page = doc.metadata.get("page", "未知")
            
            # 构建引用标识
            source_info = f"来源: {source} (P{page} Chunk{chunk_id})"
            
            # 构建上下文片段
            content = doc.page_content
            part = f"""【{source_info}】
{content}
"""
            
            # 检查长度限制
            if total_length + len(part) > self.max_context_length:
                remaining = self.max_context_length - total_length
                if remaining > 100:
                    part = part[:remaining] + "\n...（内容已截断）"
                    context_parts.append(part)
                    total_length = self.max_context_length
                    key = (source, page, chunk_id)
                    if key not in seen:
                        seen.add(key)
                        sources.append({
                            "source": source,
                            "page": page,
                            "chunk_id": chunk_id
                        })
                break
            
            context_parts.append(part)
            total_length += len(part)
            
            key = (source, page, chunk_id)
            if key not in seen:
                seen.add(key)
                sources.append({
                    "source": source,
                    "page": page,
                    "chunk_id": chunk_id
                })
        
        context = "\n".join(context_parts)
        
        # 构建完整Prompt
        prompt = f"""你是一个知识库问答助手。

请严格依据提供的上下文回答问题。

要求：
1. 不允许编造内容
2. 上下文没有答案时明确说明
3. 优先引用原文
4. 保持简洁准确

上下文：
{context}

问题：
{query}

回答："""
        
        return {
            "prompt": prompt,
            "sources": sources,
            "context_length": total_length
        }
    
    def build_summary_prompt(self, content: str) -> str:
        """
        构建摘要Prompt
        
        Args:
            content: 需要摘要的内容
            
        Returns:
            str: 摘要Prompt
        """
        return f"""请对以下内容进行总结：

{content}

要求：
1. 保持关键信息完整
2. 语言简洁明了
3. 不超过300字
"""
    
    def build_extract_prompt(self, content: str, fields: list) -> str:
        """
        构建信息抽取Prompt
        
        Args:
            content: 源内容
            fields: 需要抽取的字段列表
            
        Returns:
            str: 信息抽取Prompt
        """
        fields_str = "\n".join([f"{i+1}. {field}" for i, field in enumerate(fields)])
        
        return f"""请从以下内容中抽取指定信息：

内容：
{content}

需要抽取的字段：
{fields_str}

要求：
1. 只返回抽取结果，不要额外解释
2. 如果某字段不存在，返回"未找到"
"""


# ============================================
# 全局实例
# ============================================

# 创建默认的PromptBuilder实例
prompt_builder = PromptBuilder(max_context_length=3000)


# ============================================
# 便捷函数
# ============================================

def build_rag_prompt(query: str, docs: list) -> dict:
    """便捷函数：构建RAG问答Prompt"""
    return prompt_builder.build_rag_prompt(query, docs)
