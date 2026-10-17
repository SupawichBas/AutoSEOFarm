FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS build
WORKDIR /src
COPY ["ShopeeAffiliate.Api.csproj", "./"]
RUN dotnet restore "ShopeeAffiliate.Api.csproj"
COPY . .
RUN dotnet publish "ShopeeAffiliate.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine AS final
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "ShopeeAffiliate.Api.dll"]
